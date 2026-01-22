import base64
import binascii
import pyotp

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
    verify_cached_otp, VERIFICATION_USER_CACHE_KEY, VERIFICATION_CONTEXT_CACHE_KEY, get_context_or_session, \
    set_user_session, set_refresh_cookie, set_verification_context
from myauth.schemas import *

router = Router(tags=['A1. Login / 2FA / Forgotten Password'])
User = get_user_model()

@router.post('/totp/setup', response=TFASetupTOTPOut)
def setup_tfa_totp(request, data: TFASetupTOTPIn):
    """
    Initiate TOTP 2FA setup for the user by generating a TOTP secret and OTP URI.

    The OTP URI should be used to generate a QR code for the user to scan with their authenticator app.
    """
    context = get_context_or_session(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))
    active_device = context.get('device_id')

    if not user.twofa_enabled or user.twofa_method != TFAMethod.TOTP:
        # User has 2FA disabled raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise APIBaseError(
            title='TOTP device setup failed',
            detail='Either the given user does not have 2FA enabled or does not have the TOTP method set',
            status=status.HTTP_403_FORBIDDEN,
        )

    if active_device is not None:
        raise APIBaseError(
            title='Conflicting device found during TOTP setup',
            detail='The specified user already has an active device',
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
    """
    Confirm TOTP 2FA setup by verifying the provided passcode against the TOTP secret.
    """
    context = get_context_or_session(data.id)
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
    device, _ = TOTPDevice.objects.create(user=user, name='default')
    secret_raw = base64.b32decode(otp.secret, casefold=True)
    device.key = binascii.hexlify(secret_raw).decode('utf-8')
    device.save()

    # A new device is created, update the verification context to reflect the new device ID
    new_context = {'device_id': device.persistent_id, 'remember_me': context.get('remember_me', False)}
    new_context_id = set_verification_context(user, add_context=new_context)

    return {
        'id': new_context_id,
        'message': 'TOTP device confirmed',
    }


@router.post('/sms/send', response=TFAConfirmOut)
def send_2fa_sms(request, data: TFASetupSMSIn, purpose: UnAuthPurpose = UnAuthPurpose.LOGIN):
    """
    Send an OTP SMS to the user's registered phone number for SMS 2FA verification.
    """
    context = get_context_or_session(data.id)
    context_id = data.id
    user = get_object_or_404(User, id=context.get('user_id'))
    active_device = Device.from_persistent_id(context.get('device_id')) if context.get('device_id') else None

    if not user.twofa_enabled or user.twofa_method != TFAMethod.SMS:
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
    device, created = PhoneDevice.objects.get_or_create(
        user=user,
        number=user.phone,
    )

    # If a new phone device was created update the verification context to reflect the new device ID
    if created:
        device.name = 'default'
        device.confirmed = False
        device.save()

        new_context = {'device_id': device.persistent_id, 'remember_me': context.get('remember_me', False)}
        context_id = set_verification_context(user, add_context=new_context)

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose.value, id=context_id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose.value, id=context_id)

    # Send the OTP SMS to the phone of the user attached to the given verification context
    generate_cached_challenge(device, key_hash, key_attempts)

    return {
        'id': context_id,
        'message': 'SMS sent to registered phone number',
    }


@router.post('/verify', response=TokenOut)
def verify_2fa(request, data: TFAVerifyIn, purpose: UnAuthPurpose = UnAuthPurpose.LOGIN):
    """
    Verify the provided 2FA passcode and establish a user session upon successful verification.
    """
    context = get_context_or_session(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))

    if context.get('device_id'):
        # The user has an active device in the context
        device = Device.from_persistent_id(context.get('device_id'))
    elif user.twofa_method == TFAMethod.SMS:
        # No active device in context, but they may have a pending phone device (not possible for TOTP as the device
        # would have been created and confirmed simultaneously during setup)
        device = PhoneDevice.objects.filter(user=user, number=user.phone).first()
    else:
        device = None

    if device is None or device.user != user:
        raise APIBaseError(
            title='Encountered 2FA device error',
            detail='The provided 2FA device is invalid or does not belong to the user.',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    verify_cached_otp(device, data.id, purpose.value, data.passcode)

    if not device.confirmed:
        # Confirm the device if it was not already confirmed
        device.confirmed = True
        device.save()

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=data.id)
    key_verif_user = VERIFICATION_USER_CACHE_KEY.format(id=user.id)
    cache.delete_many([key_verif_context, key_verif_user])

    refresh = RefreshToken.for_user(user)
    persistent = context.get('remember_me', False)

    set_user_session(user, refresh, persistent)

    resp = Response({
        'access': str(refresh.access_token)
    })

    set_refresh_cookie(resp, refresh, persistent)

    return resp