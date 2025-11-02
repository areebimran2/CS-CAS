import hashlib
import secrets
import uuid

from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django_otp.models import Device
from django_otp.oath import totp
from ninja_extra import status
from two_factor.gateways import make_call, send_sms
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import totp_digits

from common.exceptions import APIBaseError
from myauth.models import User

# Verification utilities for OTP with caching
OTP_HASH_CACHE_KEY = 'otp:{purpose}:{id}:hash'
OTP_ATTEMPT_CACHE_KEY = 'otp:{purpose}:{id}:attempts'

OTP_MAX_ATTEMPTS = 5
OTP_ATTEMPT_WINDOW = 180  # 3 minutes

VERIFICATION_CONTEXT_CACHE_KEY = 'verification:context:{id}'
VERIFICATION_USER_CACHE_KEY = 'verification:user:{id}'
VERIFICATION_WINDOW = 600  # 10 minutes

def generate_cached_challenge(device: PhoneDevice, key_hash: str, key_attempts: str) -> None:
    """
    Note: This is functionally the same as PhoneDevice.generate_challenge(); however,
    this function caches the hash for the generated OTP.

    Sends the current TOTP token to `device.number` using `device.method`.

    :param device: PhoneDevice instance
    :param key_hash: The cache key to store the OTP hash
    :param key_attempts: The cache key to track OTP attempts
    :return: None
    """
    verify_allowed, _ = device.verify_is_allowed()
    if not verify_allowed:
        return None

    no_digits = totp_digits()
    token = str(totp(device.bin_key, digits=no_digits)).zfill(no_digits)
    hashed = hashlib.sha256(token.encode('utf-8')).hexdigest()
    cache.set_many({key_hash: hashed, key_attempts: 0}, OTP_ATTEMPT_WINDOW)

    if device.method == 'call':
        make_call(device=device, token=token)
    else:
        send_sms(device=device, token=token)

    return None

def verify_cached_otp(device: Device, user: User, purpose: str, passcode: str, clear: bool = True) -> None:
    """
    Verifies the provided OTP passcode against the cached hash.

    :param device: The OTP Device instance
    :param user: The User instance
    :param purpose: The purpose string for the OTP (e.g., 'change-email')
    :param passcode: The OTP passcode to verify
    :param clear: boolean flag to clear the cached data on success or not
    :return: None
    :raises APIBaseError: If verification fails
    """
    if device is None or device.user != user:
        raise APIBaseError(
            title='Encountered 2FA device error',
            detail='The provided 2FA device is invalid or does not belong to the user.',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose, id=user.id)

    hits = cache.get_many([key_hash, key_attempts])
    otp_hash = hits.get(key_hash)
    otp_attempts = hits.get(key_attempts, 0)

    if isinstance(device, PhoneDevice) and otp_hash is None:
        raise APIBaseError(
            title='SMS OTP verification error',
            detail=f'The client has not requested an OTP code or the code has expired for the following: {purpose}',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if otp_attempts >= 5:
        cache.delete_many([key_hash, key_attempts])
        raise APIBaseError(
            title='OTP retry limit exceeded',
            detail=f'The maximum number of OTP verification attempts has been exceeded for the following: {purpose}',
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    hashed_input = hashlib.sha256(passcode.encode('utf-8')).hexdigest()

    if (isinstance(device, PhoneDevice) and hashed_input != otp_hash) or not device.verify_token(passcode):
        cache.set(key_attempts, otp_attempts + 1, OTP_ATTEMPT_WINDOW)
        raise APIBaseError(
            title='OTP verification error',
            detail=f'The provided OTP code is invalid for the following: {purpose}',
            status=status.HTTP_401_UNAUTHORIZED,
            errors=[{'field': 'passcode', 'message': 'Invalid OTP code'}],
        )

    # Clear the cached metadata for OTP on successful verification
    if clear:
        cache.delete_many([key_hash, key_attempts])

    return None

def set_verification_context(user: User) -> str:
    """
    Initializes a verification context for the user and returns the context ID.

    :param user: The User instance
    :return: The verification context ID
    """
    token = secrets.token_urlsafe(16)  # Generate a secure identifier to send to the client
    verif_id = f'verif.{token}'

    # Keep track of the verification context in the cache, the user id is mapped back to the token to ensure the
    # user has only one active verification session at a time.
    context_cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=verif_id)  # Link the token to the user ID
    user_cache_key = VERIFICATION_USER_CACHE_KEY.format(id=user.id)  # Link the user ID to the token

    # Invalidate any existing verification context for the user
    cache.delete_many([cache.get(user_cache_key), user_cache_key])

    cache.set_many({context_cache_key: user.id, user_cache_key: verif_id}, VERIFICATION_WINDOW)

    return verif_id

def get_verification_context(context_id: str) -> uuid.UUID:
    """
    Retrieves the user ID associated with the given verification context ID.

    :param context_id: The verification context ID
    :return: The user ID
    :raises APIBaseError: If the context is invalid or expired
    """
    context_cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=context_id)
    user_id = cache.get(context_cache_key)

    if user_id is None:
        raise APIBaseError(
            title='User verification context error',
            detail=f'The client has not established a valid verification context for a user, or it has expired.',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return user_id

def validate_new_password(user: User, password: str) -> None:
    """
    Validates the provided password against the user's stored password.

    :param user: The User instance
    :param password: The password to validate
    :return: None
    :raises APIBaseError: If the password does not meet the policy requirements
    """
    try:
        validate_password(password, user=user)
    except ValidationError as e:
        raise APIBaseError(
            title='Password validation error',
            detail='The provided new password does not meet the password policy requirements',
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=[{'field': 'new_password', 'messages': e.messages}],
        )

    return None

# Phone change utilities
PHONE_CHANGE_CACHE_KEY = 'phone-change:{id}'
PHONE_CHANGE_WINDOW = 300  # 5 minutes

PHONE_CHANGE_OLD_VERIFIED = 'old-verified'
PHONE_CHANGE_NEW_AWAITING = 'new-awaiting-verification'

# Forgot password utilities
RESET_TOKEN_CACHE_KEY = 'reset-token:{id}'
RESET_TOKEN_WINDOW = 900  # 15 minutes