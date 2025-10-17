import hashlib
import uuid

from django.core.cache import cache
from django_otp.models import Device
from django_otp.oath import totp
from ninja.errors import AuthenticationError, HttpError
from two_factor.gateways import make_call, send_sms
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import totp_digits

from myauth.models import User

# Common caching utilities
OTP_HASH_CACHE_KEY = 'otp:{purpose}:{id}:hash'
OTP_ATTEMPT_CACHE_KEY = 'otp:{purpose}:{id}:attempts'

OTP_MAX_ATTEMPTS = 5
OTP_ATTEMPT_WINDOW = 180  # 3 minutes

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

def verify_cached_otp(device: Device, user: User, purpose: str, passcode: str) -> None:
    """
    Verifies the provided OTP passcode against the cached hash.

    :param device: The OTP Device instance
    :param user: The User instance
    :param purpose: The purpose string for the OTP (e.g., 'change-email')
    :param passcode: The OTP passcode to verify
    :return: None
    :raises AuthenticationError: If verification fails
    """
    if device is None or device.user != user:
        raise AuthenticationError()

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose, id=user.id)

    otp_hash = cache.get(key_hash)
    otp_attempts = cache.get(key_attempts, 0)

    if otp_hash is None:
        raise AuthenticationError()

    if otp_attempts >= 5:
        cache.delete_many([key_hash, key_attempts])
        raise HttpError(429, 'Too many attempts. Please request a new code.')

    hashed_input = hashlib.sha256(passcode.encode('utf-8')).hexdigest()

    if (isinstance(device, PhoneDevice) and hashed_input != otp_hash) or not device.verify_token(passcode):
        cache.set(key_attempts, otp_attempts + 1, OTP_ATTEMPT_WINDOW)
        raise AuthenticationError()

    # Clear the cached metadata for OTP on successful verification
    cache.delete_many([key_hash, key_attempts])

    return None

# Phone change utilities
PHONE_CHANGE_CACHE_KEY = 'phone-change:{id}'
PHONE_CHANGE_WINDOW = 300  # 5 minutes

PHONE_CHANGE_OLD_VERIFIED = 'old-verified'
PHONE_CHANGE_NEW_AWAITING = 'new-awaiting-verification'