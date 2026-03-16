import base64
import binascii
from typing import Dict, Any

import pyotp

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.tokens import RefreshToken
from two_factor.plugins.phonenumber.models import PhoneDevice

from common.exceptions import APIBaseError
from myauth.services.otp import (
    generate_cached_challenge, OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, verify_cached_otp,
)
from myauth.services.verification import (
    VERIFICATION_USER_CACHE_KEY, VERIFICATION_CONTEXT_CACHE_KEY,
    get_context_or_session, set_verification_context,
)
from myauth.services.session import set_user_session, set_refresh_cookie

User = get_user_model()


def setup_totp(context_id: str, tfa_method_totp: str) -> Dict[str, str]:
    """
    Initiate TOTP 2FA setup — generate a TOTP secret and OTP URI.

    :param context_id: The verification context ID
    :param tfa_method_totp: The string value of TFAMethod.TOTP for comparison
    :return: dict with 'id' and 'otpauth_url'
    """
    context = get_context_or_session(context_id)
    user = get_object_or_404(User, id=context.get('user_id'))
    active_device = context.get('device_id')

    if not user.twofa_enabled or user.twofa_method != tfa_method_totp:
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
        'id': context_id,
        'otpauth_url': otp_uri
    }


def confirm_totp(context_id: str, url: str, passcode: str) -> Dict[str, str]:
    """
    Confirm TOTP 2FA setup by verifying the passcode against the TOTP secret.

    :param context_id: The verification context ID
    :param url: The OTP URI containing the secret
    :param passcode: The TOTP passcode to verify
    :return: dict with 'id' (new context) and 'message'
    """
    context = get_context_or_session(context_id)
    user = get_object_or_404(User, id=context.get('user_id'))
    otp = pyotp.parse_uri(url)  # Extract the OTP info from the provided URI (secret, name, etc.)

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
    if not totp.verify(passcode):
        return APIBaseError(
            title='Invalid TOTP passcode',
            status=status.HTTP_401_UNAUTHORIZED,
            errors=[{'field': 'passcode'}],
        )

    # Successfully verified, create and save the TOTP device for the user
    device = TOTPDevice.objects.create(user=user, name='default')
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


def send_sms_otp(context_id: str, purpose_value: str, tfa_method_sms: str) -> Dict[str, str]:
    """
    Send an OTP SMS to the user's registered phone number for SMS 2FA verification.

    :param context_id: The verification context ID
    :param purpose_value: The purpose string value (e.g., 'login')
    :param tfa_method_sms: The string value of TFAMethod.SMS for comparison
    :return: dict with 'id' (context_id) and 'message'
    """
    context = get_context_or_session(context_id)
    result_context_id = context_id
    user = get_object_or_404(User, id=context.get('user_id'))
    active_device = Device.from_persistent_id(context.get('device_id')) if context.get('device_id') else None

    if not user.twofa_enabled or user.twofa_method != tfa_method_sms:
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
        result_context_id = set_verification_context(user, add_context=new_context)

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose_value, id=result_context_id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose_value, id=result_context_id)

    # Send the OTP SMS to the phone of the user attached to the given verification context
    generate_cached_challenge(device, key_hash, key_attempts)

    return {
        'id': result_context_id,
        'message': 'SMS sent to registered phone number',
    }


def verify_2fa_and_create_session(context_id: str, passcode: str, purpose_value: str,
                                   tfa_method_sms: str) -> Response:
    """
    Verify the provided 2FA passcode and establish a user session upon successful verification.

    :param context_id: The verification context ID
    :param passcode: The OTP passcode to verify
    :param purpose_value: The purpose string value (e.g., 'login')
    :param tfa_method_sms: The string value of TFAMethod.SMS for comparison
    :return: Response with access token and refresh cookie
    """
    context = get_context_or_session(context_id)
    user = get_object_or_404(User, id=context.get('user_id'))

    if context.get('device_id'):
        # The user has an active device in the context
        device = Device.from_persistent_id(context.get('device_id'))
    elif user.twofa_method == tfa_method_sms:
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

    verify_cached_otp(device, context_id, purpose_value, passcode)

    if not device.confirmed:
        # Confirm the device if it was not already confirmed
        device.confirmed = True
        device.save()

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=context_id)
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

