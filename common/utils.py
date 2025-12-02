import hashlib
import secrets
from types import SimpleNamespace
from typing import Optional, Dict, Any, Callable

from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.module_loading import import_string
from django_otp.models import Device
from django_otp.oath import totp
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.tokens import Token
from pydantic_extra_types.phone_numbers import PhoneNumber
from two_factor.gateways import make_call, send_sms
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import totp_digits

from common.exceptions import APIBaseError
from myauth.models import User
from cs_cas import settings

# Verification utilities for OTP with caching
OTP_HASH_CACHE_KEY = 'otp:{purpose}:{id}:hash'
OTP_ATTEMPT_CACHE_KEY = 'otp:{purpose}:{id}:attempts'
OTP_MAX_ATTEMPTS = 5
OTP_ATTEMPT_WINDOW = 180  # 3 minutes

# User verification context utilities
VERIFICATION_CONTEXT_CACHE_KEY = 'verification:context:{id}'
VERIFICATION_USER_CACHE_KEY = 'verification:user:{id}'
VERIFICATION_WINDOW = 600  # 10 minutes

# User logged-in session utilities
SESSION_USER_CACHE_KEY = 'session:user:{id}'
SESSION_IDLE_WINDOW = 7 * 24 * 3600  # For remembered sessions, idle timeout after 7 days
SESSION_TIMEOUT = 3600  # For non-remembered sessions, timed out after 1 hour of inactivity

# Phone change utilities
PHONE_CHANGE_CACHE_KEY = 'phone-change:{id}'
PHONE_CHANGE_OLD_VERIFIED = 'old-verified'
PHONE_CHANGE_NEW_AWAITING = 'new-awaiting-verification'
PHONE_CHANGE_WINDOW = 300  # 5 minutes

# Forgot password utilities
RESET_TOKEN_CACHE_KEY = 'reset-token:{id}'
RESET_TOKEN_WINDOW = 900  # 15 minutes


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
    #TODO: use more secure hashing like HMAC
    hashed = hashlib.sha256(token.encode('utf-8')).hexdigest()
    cache.set_many({key_hash: hashed, key_attempts: 0}, OTP_ATTEMPT_WINDOW)

    if device.method == 'call':
        make_call(device=device, token=token)
    else:
        send_sms(device=device, token=token)

    return None


def generate_cached_code(phone: PhoneNumber, key_hash: str, key_attempts: str, digits: int = 6) -> None:
    """
    Sends an SMS code to the specified phone number. Used for all secure actions that an authenticated user may
    perform that require verification via SMS.

    :param phone: The phone number to send the SMS code to
    :param key_hash: The cache key to store the OTP hash
    :param key_attempts: The cache key to track OTP attempts
    :param digits: The number of digits for the OTP code
    :return: None
    """
    token = f'{secrets.randbelow(10 ** digits):0{digits}d}'
    # TODO: use more secure hashing like HMAC
    hashed = hashlib.sha256(token.encode('utf-8')).hexdigest()
    cache.set_many({key_hash: hashed, key_attempts: 0}, OTP_ATTEMPT_WINDOW)

    device = SimpleNamespace(number=phone)
    send_sms(device=device, token=token)

    return None


def _verify_cached_common(*, cache_id: str, purpose: str, passcode: str, clear: bool = True,
                          require_cached_hash: bool = True, check: Callable[[str, Optional[str]], bool]) -> None:
    """
    Unified verifier for:
      - cache-only SMS codes (check compares to cached_hash)
      - device-based OTP (check calls device.verify_token, e.g., TOTPDevice)
      - hybrid flows (check uses both, e.g., PhoneDevice with hashed cached code)

    Note: Devices are used for authentication while sms codes are used for secure actions.

    :param cache_id: The cache key ID (e.g., user ID for SMS codes, verification context ID for PhoneDevice codes)
    :param purpose: The purpose string for the OTP (e.g., 'login', 'change-email')
    :param passcode: The OTP passcode to verify
    :param clear: boolean flag to clear the cached data on success or not
    :param require_cached_hash: Whether a cached hash is required for verification (not required for TOTPDevice)
    :param check: A callable that takes (passcode, cached_hash) and returns True if valid, False otherwise
    :return: None
    """
    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose, id=cache_id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose, id=cache_id)

    hits = cache.get_many([key_hash, key_attempts])
    cached_hash = hits.get(key_hash)
    attempts = hits.get(key_attempts, 0)

    # Unified errors
    # Cached hash required but not found
    if require_cached_hash and cached_hash is None:
        raise APIBaseError(
            title="Verification failed",
            detail=f"No active verification code for: {purpose}.",
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Too many attempts
    if attempts >= OTP_MAX_ATTEMPTS:
        cache.delete_many([key_hash, key_attempts])
        raise APIBaseError(
            title="Too many attempts",
            detail=f"Retry limit exceeded for: {purpose}.",
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Check the provided passcode
    if not check(passcode, cached_hash):
        cache.set(key_attempts, attempts + 1, OTP_ATTEMPT_WINDOW)
        raise APIBaseError(
            title="Verification failed",
            detail=f"Invalid verification code for: {purpose}.",
            status=status.HTTP_401_UNAUTHORIZED,
            errors=[{"field": "passcode", "message": "Invalid code"}],
        )

    # Clear the cache on successful verification
    if clear:
        cache.delete_many([key_hash, key_attempts])


def verify_cached_otp(device: Device, context_id: str, purpose: str, passcode: str, clear: bool = True) -> None:
    """
    Verifies the provided OTP passcode.

    :param device: The OTP Device instance
    :param context_id: The verification context ID
    :param purpose: The purpose string for the OTP (e.g., 'login')
    :param passcode: The OTP passcode to verify
    :param clear: boolean flag to clear the cached data on success or not
    :return: None
    """
    is_phone = isinstance(device, PhoneDevice)

    def verifier(code: str, cached_hash: Optional[str]) -> bool:
        if is_phone:
            hashed_input = hashlib.sha256(code.encode('utf-8')).hexdigest()
            return hashed_input == cached_hash and device.verify_token(code)
        else:
            return device.verify_token(code)

    _verify_cached_common(
        cache_id=context_id,
        purpose=purpose,
        passcode=passcode,
        clear=clear,
        require_cached_hash=is_phone,
        check=verifier,
    )


def verify_cached_code(user: User, purpose: str, passcode: str, clear: bool = True) -> None:
    """
    Verifies the provided SMS code.

    :param user: The User instance
    :param purpose: The purpose string for the OTP (e.g., 'change-email')
    :param passcode: The SMS code to verify
    :param clear: boolean flag to clear the cached data on success or not
    :return: None
    """

    def verifier(code: str, cached_hash: Optional[str]) -> bool:
        hashed_input = hashlib.sha256(code.encode('utf-8')).hexdigest()
        return hashed_input == cached_hash

    _verify_cached_common(
        cache_id=str(user.id),
        purpose=purpose,
        passcode=passcode,
        clear=clear,
        require_cached_hash=True,
        check=verifier,
    )


def set_verification_context(user: User, add_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Initializes a verification context for the user and returns the context ID. The context is typically just the user
    ID, but additional context information can be added as needed.

    :param user: The User instance
    :param add_context: Additional Context information to store (e.g., device_id, remember_me)
    :return: The verification context ID
    """
    token = secrets.token_urlsafe(16)  # Generate a secure identifier to send to the client
    verif_id = f'verif.{token}'

    # Keep track of the verification context in the cache, the user id is mapped back to the token to ensure the
    # user has only one active verification session at a time.
    context_cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=verif_id)  # Link the token to the user ID
    user_cache_key = VERIFICATION_USER_CACHE_KEY.format(id=user.id)  # Link the user ID to the token

    # Check for existing verification context
    existing_cache_id = cache.get(user_cache_key)
    existing_cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=existing_cache_id) if existing_cache_id else None

    # Invalidate any existing verification context for the user
    cache.delete_many([existing_cache_key])

    context = {'user_id': user.id}

    if add_context:
        context |= add_context

    cache.set_many({context_cache_key: context, user_cache_key: verif_id}, VERIFICATION_WINDOW)

    return verif_id


def set_user_session(user: User, token: Token, remember_me: bool, old: Optional[Token] = None) -> None:
    """
    Creates or updates a logged-in session for the user.

    Note: It is assumed that if old is provided, it corresponds to an existing valid session that is to be updated.
          Otherwise, a new session is created. Additionally, the user ID claim in the old token must match the provided
          user ID.

    :param user: The User instance
    :param token: The authentication token (JWT)
    :param remember_me: Whether the user opted for a persistent session
    :param old: The old authentication token (JWT) if updating an existing session
    :return: None
    """
    if old:
        assert str(user.id) == old['uid'], 'Old token user ID does not match the provided user ID'
        session_id = old['sid']
    else:
        secure_id = secrets.token_urlsafe(16)  # Generate a secure identifier
        session_id = f'session.{secure_id}'

    # Keep track of the logged-in session state
    user_cache_key = SESSION_USER_CACHE_KEY.format(id=user.id)

    # TODO: If we want to support multiple sessions per user, do to following:
    #   1. Create a separate record for each session (e.g., SESSION_CACHE_KEY). This would map session_id to
    #      session data (user id, jti, remember_me, etc.)
    #   2. SESSION_USER_CACHE_KEY would be changed to maintain a set of active session IDs for the user (adds a lot of
    #      memory overhead, can bound # of sessions). Alternatively, we can maintain the "user version" and simply
    #      invalidate all sessions when the version is incremented (e.g., on password change).

    # For simplicity, we only track the latest session for the user
    context = {
        'session_id': session_id,
        'jti': token['jti'],
        'remember_me': remember_me,
    }

    remaining_abs = max(0, token['exp'] - timezone.now().timestamp())  # absolute remaining time of token validity

    # Store the session with appropriate timeout
    if remember_me:
        cache.set_many({user_cache_key: context}, remaining_abs)
    else:
        cache.set_many({user_cache_key: context}, min(SESSION_TIMEOUT, remaining_abs))

    token['uid'] = str(user.id)
    token['sid'] = session_id


def get_context_or_session(cache_id: str) -> Dict[str, Any]:
    """
    Helper function to retrieve either a verification context or user session based on the cache key pattern.

    :param cache_id: The cache key ID (either verification context ID or user ID for session)
    :return: The retrieved context or session information
    :raises APIBaseError: If the context or session is invalid or expired
    """
    if cache_id.startswith('verif'):
        cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=cache_id)
        err_message = 'The client has not established a valid verification context for a user, or it has expired.'
    else:
        cache_key = SESSION_USER_CACHE_KEY.format(id=cache_id)
        err_message = 'The client has not established a valid session for the given user, or it has expired.'

    data = cache.get(cache_key)

    if data is None:
        raise APIBaseError(
            title='User verification context or session error',
            detail=err_message,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return data


def set_refresh_cookie(response: Response, token: Token, remember_me: bool) -> None:
    """
    Sets the refresh token in an HTTP-only cookie on the response.

    :param response: The Response instance
    :param token: The refresh Token instance
    :param remember_me: Whether the user opted for a persistent session
    :return: None
    """
    if remember_me:
        # maintain persistent session between browser restarts, but not beyond the token expiry
        remaining_abs = max(0, token['exp'] - timezone.now().timestamp())  # absolute remaining time of token validity
        max_age = max(0, min(remaining_abs, SESSION_IDLE_WINDOW) - 60)  # small expiry safety margin
    else:
        # session cookie, expires when client shuts down
        max_age = None

    response.set_cookie(
        key=settings.REFRESH_COOKIE_KEY,
        value=str(token),
        max_age=max_age,
        httponly=True,
        secure=not settings.DEBUG,
        # 'Strict' if on same domain, 'None' if cross-site
        samesite='Strict',
    )


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



def not_implemented():
    """
    Raises a 501 Not Implemented response for stubbed endpoints.
    """
    raise APIBaseError(
        title='Not Implemented',
        status=status.HTTP_501_NOT_IMPLEMENTED,
        detail='This endpoint is stubbed. Fill in the handler logic.',
    )
