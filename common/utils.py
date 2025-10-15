import hashlib
import uuid

from django.core.cache import cache
from django_otp.oath import totp
from two_factor.gateways import make_call, send_sms
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import totp_digits

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