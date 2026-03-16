import hashlib
import secrets
from types import SimpleNamespace
from typing import Optional, Callable

from django.core.cache import cache
from django_otp.models import Device
from django_otp.oath import totp
from ninja_extra import status
from pydantic_extra_types.phone_numbers import PhoneNumber
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

