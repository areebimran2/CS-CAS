import base64
import pyotp
import binascii

from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from ninja import Router, PatchDict
from ninja.errors import AuthenticationError, HttpError
from ninja.responses import Response
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device

from common.utils import generate_cached_challenge, OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, OTP_ATTEMPT_WINDOW, \
    verify_cached_otp, PHONE_CHANGE_CACHE_KEY, PHONE_CHANGE_WINDOW, PHONE_CHANGE_OLD_VERIFIED, PHONE_CHANGE_NEW_AWAITING
from myauth.schemas import *

router = Router()
User = get_user_model()

@router.post('/login', response=LoginOut)
def login(request, data: LoginIn):
    user: Optional[User] = authenticate(username=data.email, password=data.password)
    if user is None:
        AuthenticationError()

    device = default_device(user)

    return {
        'id': user.id,
        'method': device
    }


@router.post('/2fa/totp/setup', response=TFASetupTOTPOut)
def setup_tfa_totp(request, data: TFASetupIn):
    user = get_object_or_404(User, id=data.id)
    active_device = default_device(user)

    if not user.twofa_enabled or user.twofa_method != 'totp':
        # User has 2FA disabled raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise AuthenticationError()

    if active_device is not None:
        raise HttpError(409, 'User already has an active 2FA device')

    # Generate a potential TOTP device secret
    secret = pyotp.random_base32()

    # Build the OTP URI (for QR code rendering on the client side)
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="UTC-CS-CAS"
    )

    return {
        'id': user.id,
        'otpauth_url': otp_uri
    }


@router.post('/2fa/totp/confirm', response=TFAConfirmOut)
def confirm_tfa_totp(request, data: TFAConfirmTOTPIn, purpose: str = 'login'):
    user = get_object_or_404(User, id=data.id)
    otp = pyotp.parse_uri(data.url)

    if user.email != otp.name:
        raise AuthenticationError()

    totp = pyotp.TOTP(otp.secret)
    if not totp.verify(data.passcode):
        return Response({'message': 'Invalid code'}, status=401)

    device, _ = TOTPDevice.objects.get_or_create(user=user)
    secret_raw = base64.b32decode(otp.secret, casefold=True)
    device.key = binascii.hexlify(secret_raw).decode('utf-8')
    device.save()

    # TOTP devices do not require caching the OTP hash, only attempts
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose, id=user.id)
    cache.set(key_attempts, 0, OTP_ATTEMPT_WINDOW)

    return {
        'id': user.id,
        'device_id': device.persistent_id,
        'message': 'TOTP device confirmed'
    }


@router.post('/2fa/sms/send', response=TFAConfirmOut)
def send_2fa_sms(request, data: TFASetupIn, purpose: str = 'login'):
    user = get_object_or_404(User, id=data.id)
    active_device = default_device(user)

    if not user.twofa_enabled or user.twofa_method != 'sms':
        # User has 2FA disabled, raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise AuthenticationError()

    if isinstance(active_device, TOTPDevice):
        raise HttpError(409, 'User has an active TOTP device')

    # Create a record to maintain the User's OTP Phone Device
    device, _ = PhoneDevice.objects.get_or_create(
        user=user,
        number=user.phone,
    )

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose, id=user.id)

    # Send the OTP SMS to the user's phone
    generate_cached_challenge(device, key_hash, key_attempts)

    return {
        'id': user.id,
        'device_id': device.persistent_id,
        'message': 'SMS sent to registered phone number'
    }


@router.post('/2fa/verify', response=TFAVerifyOut)
def verify_2fa(request, data: TFAVerifyIn, purpose: str = 'login'):
    user = get_object_or_404(User, id=data.id)
    device = Device.from_persistent_id(data.device_id)

    verify_cached_otp(device, user, purpose, data.passcode)

    if default_device(user) is None:
        device.name = 'default'
        device.save()

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@router.get('/me', response=UserSchema, auth=JWTAuth())
def profile(request):
    user: User = request.auth
    return user


@router.patch('/me', response=UserSchema, auth=JWTAuth())
def update_profile(request, data: PatchDict[UserBasicUpdateSchema]):
    user: User = request.auth

    for attr, value in data.items():
        setattr(user, attr, value)

    user.save()

    return user


@router.post('/me/security/sms/send', response=MessageOut, auth=JWTAuth())
def secure_action(request, data: SecuritySetupIn):
    user: User = request.auth
    device = default_device(user) # Assume that every user has SMS 2FA enabled

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)

    # Send the OTP SMS to the user's phone
    generate_cached_challenge(device, key_hash, key_attempts)

    return {
        'message': 'SMS sent to registered phone number'
    }


@router.post('/me/phone/verify-old', response=MessageOut, auth=JWTAuth())
def verify_old_phone(request, data: VerifySchema, purpose: Purpose = Purpose.VERIFY_OLD_PHONE):
    user: User = request.auth
    device = default_device(user)

    verify_cached_otp(device, user, purpose.value, data.passcode)

    phone_change_key = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    cache.set(phone_change_key, PHONE_CHANGE_OLD_VERIFIED, PHONE_CHANGE_WINDOW)

    return {
        'message': 'Old phone number verified'
    }

@router.patch('/me/phone/change', response=MessageOut, auth=JWTAuth())
def change_phone(request, data: ChangePhoneIn, purpose: Purpose = Purpose.VERIFY_NEW_PHONE):
    user: User = request.auth

    phone_change_key = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    if cache.get(phone_change_key) != PHONE_CHANGE_OLD_VERIFIED:
        raise HttpError(400, 'Old phone number not verified')

    temp_device = PhoneDevice(
        user=user,
        number=data.phone,
    )

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose.value, id=user.id)

    generate_cached_challenge(temp_device, key_hash, key_attempts)

    cache.set(phone_change_key, {
        'status': PHONE_CHANGE_NEW_AWAITING,
        'device_key': temp_device.key,
        'number': data.phone,
    }, PHONE_CHANGE_WINDOW)

    return {
        'message': 'OTP sent to new phone number'
    }



@router.post('/me/phone/verify-new', response=MessageOut, auth=JWTAuth())
def verify_new_phone(request, data: VerifySchema, purpose: Purpose = Purpose.VERIFY_NEW_PHONE):
    user: User = request.auth
    device = default_device(user)

    phone_change_key = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(phone_change_key)

    if phone_change['status'] != PHONE_CHANGE_NEW_AWAITING:
        raise HttpError(400, 'New phone number change not initiated or old phone not verified')

    temp_device = PhoneDevice(
        key=phone_change['device_key'],
        user=user,
        number=phone_change['number'],
    )

    verify_cached_otp(temp_device, user, purpose.value, data.passcode)

    # Clear the phone change cache key after successful verification
    cache.delete(phone_change_key)

    user.phone = phone_change['number']
    device.number = phone_change['number']

    user.save()
    device.save()

    return {
        'message': 'New phone number verified, phone number updated'
    }
