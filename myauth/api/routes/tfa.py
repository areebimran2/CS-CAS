import base64
import binascii
import pyotp

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_otp import devices_for_user
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from ninja import Router
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.tokens import RefreshToken
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from common.utils import generate_cached_challenge, OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, \
    verify_cached_otp, VERIFICATION_USER_CACHE_KEY, VERIFICATION_CONTEXT_CACHE_KEY, get_verification_context
from cs_cas import settings
from myauth.schemas import *

router = Router(tags=['TFA'])
User = get_user_model()

@router.post('/totp/setup', response=TFASetupTOTPOut)
def setup_tfa_totp(request, data: TFASetupTOTPIn):
    """
    Initiate TOTP 2FA setup for the user by generating a TOTP secret and OTP URI.

    The OTP URI should be used to generate a QR code for the user to scan with their authenticator app.
    """
    context = get_verification_context(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))
    active_device = Device.from_persistent_id(context.get('device_id'))

    if not user.twofa_enabled or user.twofa_method != 'totp':
        # User has 2FA disabled raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise APIBaseError(
            title='TOTP device setup failed',
            detail='Either the given user does not have 2FA enabled or does not have the TOTP method set',
            status=status.HTTP_403_FORBIDDEN,
        )

    if active_device is not None:
        device_type = active_device.__class__.__name__
        raise APIBaseError(
            title='User already has an active device',
            detail=f'Device type and set method is: {device_type} and {user.twofa_method} respectively (should match)',
            status=status.HTTP_409_CONFLICT,
        )

    # Generate a potential TOTP device secret
    secret = pyotp.random_base32()

    # Build the OTP URI (for QR code rendering on the client side)
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="cscas-api"
    )

    return {
        'id': data.id,
        'otpauth_url': otp_uri
    }


@router.post('/totp/confirm', response=TFAConfirmOut)
def confirm_tfa_totp(request, data: TFAConfirmTOTPIn):
    context = get_verification_context(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))
    otp = pyotp.parse_uri(data.url) # Extract the OTP info from the provided URI (secret, name, etc.)

    # Validate that the OTP URI corresponds to the user
    if user.email != otp.name:
        raise APIBaseError(
            title='Bad OTP URL for user',
            detail='The provided OTP URL does not correspond to the given user',
            status=status.HTTP_400_BAD_REQUEST,
            errors=[{'field': 'url', 'message': 'OTP URL does not match user email'}],
        )

    # Verify the provided passcode against the TOTP secret
    totp = pyotp.TOTP(otp.secret)
    if not totp.verify(data.passcode):
        return APIBaseError(
            title='Invalid TOTP passcode',
            status=status.HTTP_401_UNAUTHORIZED,
            errors=[{'field': 'passcode'}],
        )

    # Successfully verified, create and save the TOTP device for the user
    device, _ = TOTPDevice.objects.get_or_create(user=user)
    secret_raw = base64.b32decode(otp.secret, casefold=True)
    device.key = binascii.hexlify(secret_raw).decode('utf-8')
    device.save()

    return {
        'id': data.id,
        'message': 'TOTP device confirmed',
    }


@router.post('/sms/send', response=TFAConfirmOut)
def send_2fa_sms(request, data: TFASetupSMSIn):
    context = get_verification_context(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))
    active_device = Device.from_persistent_id(context.get('device_id'))

    if not user.twofa_enabled or user.twofa_method != 'sms':
        # User has 2FA disabled, raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise APIBaseError(
            title='SMS device setup failed',
            detail='Either the given user does not have 2FA enabled or does not have the SMS method set',
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(active_device, TOTPDevice):
        raise APIBaseError(
            title='Conflicting 2FA device found',
            detail=f'The users 2FA method is: {user.twofa_method}; this must also be TOTP',
            status=status.HTTP_409_CONFLICT,
        )

    # Create a record to maintain the User's OTP Phone Device
    device, _ = PhoneDevice.objects.get_or_create(
        user=user,
        number=user.phone,
    )

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)

    # Send the OTP SMS to the user's phone
    generate_cached_challenge(device, key_hash, key_attempts)

    return {
        'id': data.id,
        'message': 'SMS sent to registered phone number',
    }


@router.post('/verify', response=TFAVerifyOut)
def verify_2fa(request, data: TFAVerifyIn):
    context = get_verification_context(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))
    device = Device.from_persistent_id(context.get('device_id'))

    verify_cached_otp(device, user, data.purpose.value, data.passcode)

    if default_device(user) is None:
        device.name = 'default'
        device.save()

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=data.id)
    key_verif_user = VERIFICATION_USER_CACHE_KEY.format(id=user.id)

    cache.delete_many([key_verif_context, key_verif_user])

    refresh = RefreshToken.for_user(user)

    resp = Response({
        'access': str(refresh.access_token)
    })
    resp.set_cookie(
        key=settings.REFRESH_COOKIE_KEY,
        value=str(refresh),
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Strict',
    )

    return resp