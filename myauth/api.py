import base64
import pyotp
import binascii

from typing import Optional
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django_otp import devices_for_user
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from ninja import Router
from ninja.errors import AuthenticationError
from ninja.responses import Response
from ninja_jwt.schema import TokenObtainPairOutputSchema
from ninja_jwt.tokens import RefreshToken, AccessToken
from two_factor.plugins.phonenumber.models import PhoneDevice

from myauth.schemas import *

router = Router()
User = get_user_model()

@router.post('/login', response=LoginOut)
def login(request, data: LoginIn):
    user: Optional[User] = authenticate(username=data.email, password=data.password)
    if user is None:
        AuthenticationError()

    devices = list(devices_for_user(user))

    return {
        'id': user.id,
        'methods': devices
    }

@router.post('/2fa/totp/setup', response=TFASetupTOTPOut)
def setup_tfa_totp(request, data: TFASetupIn):
    user = get_object_or_404(User, id=data.id)
    devices = list(devices_for_user(user))

    if not user.twofa_enabled or user.twofa_method != 'totp' or len(devices) > 0:
        # User either has 2FA disabled, or already has a device, raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise AuthenticationError()

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
def confirm_tfa_totp(request, data: TFAConfirmTOTPIn):
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

    return {
        'id': user.id,
        'device_id': device.persistent_id,
        'message': 'TOTP device confirmed'
    }

@router.post('/2fa/sms/send', response=TFAConfirmOut)
def send_2fa_sms(request, data: TFASetupIn):
    user = get_object_or_404(User, id=data.id)
    devices = list(devices_for_user(user))

    if not user.twofa_enabled or user.twofa_method != 'sms' or len(devices) > 1:
        # User has 2FA disabled, raise an error
        # May also want to raise an error if the user has a different 2FA method enabled or
        # has both SMS and TOTP devices
        raise AuthenticationError()

    # Create a record to maintain the User's OTP Phone Device
    device, _ = PhoneDevice.objects.get_or_create(
        user=user,
        number=user.phone,
    )

    # Send the OTP SMS to the user's phone
    device.generate_challenge()

    return {
        'id': user.id,
        'device_id': device.persistent_id,
        'message': 'SMS sent to registered phone number'
    }


@router.post('/2fa/verify', response=TFAVerifyOut)
def verify_2fa(request, data: TFAVerifyIn):
    user = get_object_or_404(User, id=data.id)
    device =  Device.from_persistent_id(data.device_id)

    if device is None or device.user != user:
        raise AuthenticationError()

    if not device.verify_token(data.passcode):
        raise AuthenticationError()

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


