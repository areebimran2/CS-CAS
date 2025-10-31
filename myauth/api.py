import base64
import hashlib
import pyotp
import binascii

from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django_otp import devices_for_user
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from ninja import Router, PatchDict
from ninja.errors import AuthenticationError, HttpError, ValidationError
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from common.utils import generate_cached_challenge, OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, \
    verify_cached_otp, PHONE_CHANGE_CACHE_KEY, PHONE_CHANGE_WINDOW, PHONE_CHANGE_OLD_VERIFIED, \
    PHONE_CHANGE_NEW_AWAITING, RESET_TOKEN_WINDOW, RESET_TOKEN_CACHE_KEY, VERIFICATION_USER_CACHE_KEY, \
    VERIFICATION_CONTEXT_CACHE_KEY, VERIFICATION_WINDOW, set_verification_context, get_verification_context
from myauth.schemas import *

router = Router()
User = get_user_model()

@router.post('/login', response=LoginOut)
def login(request, data: LoginIn):
    """
    Check if user credentials are valid and return user ID and 2FA method.

    If the user has not yet setup 2FA, then they must do so after this step by calling the appropriate 2FA setup
    endpoint (SMS default). Otherwise, they can proceed to verify 2FA using the returned method/device.
    """
    user: Optional[User] = authenticate(username=data.email, password=data.password)
    if user is None: # Invalid credentials
        raise APIBaseError(
            title='Invalid credentials',
            status=status.HTTP_401_UNAUTHORIZED,
            detail='Either email or password is invalid',
            errors=[{'field': 'email'}, {'field': 'password'}]
        )

    device = default_device(user)

    context_id = set_verification_context(user)

    return {
        'id': context_id,
        'method': device
    }


@router.post('/2fa/totp/setup', response=TFASetupTOTPOut)
def setup_tfa_totp(request, data: TFASetupTOTPIn):
    """
    Initiate TOTP 2FA setup for the user by generating a TOTP secret and OTP URI.

    The OTP URI should be used to generate a QR code for the user to scan with their authenticator app.
    """
    user_id = get_verification_context(data.id)
    user = get_object_or_404(User, id=user_id)
    active_device = default_device(user)

    if not user.twofa_enabled or user.twofa_method != 'totp':
        # User has 2FA disabled raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise APIBaseError(
            title='Either the given user does not have 2FA enabled or does not have the TOTP method set',
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
        issuer_name="UTC-CS-CAS"
    )

    return {
        'id': data.id,
        'otpauth_url': otp_uri
    }


@router.post('/2fa/totp/confirm', response=TFAConfirmOut)
def confirm_tfa_totp(request, data: TFAConfirmTOTPIn):
    user_id = get_verification_context(data.id)
    user = get_object_or_404(User, id=user_id)
    otp = pyotp.parse_uri(data.url) # Extract the OTP info from the provided URI (secret, name, etc.)

    # Validate that the OTP URI corresponds to the user
    if user.email != otp.name:
        raise APIBaseError(
            title='The provided OTP URI does not correspond to the given user',
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify the provided passcode against the TOTP secret
    totp = pyotp.TOTP(otp.secret)
    if not totp.verify(data.passcode):
        return APIBaseError(
            title='Invalid TOTP passcode',
            status=status.HTTP_401_UNAUTHORIZED,
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


@router.post('/2fa/sms/send', response=TFAConfirmOut)
def send_2fa_sms(request, data: TFASetupSMSIn):
    user_id = get_verification_context(data.id)
    user = get_object_or_404(User, id=user_id)
    active_device = default_device(user)

    if not user.twofa_enabled or user.twofa_method != 'sms':
        # User has 2FA disabled, raise an error
        # May also want to raise an error if the user has a different 2FA method enabled
        raise APIBaseError(
            title='Either the given user does not have 2FA enabled or does not have the SMS method set',
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(active_device, TOTPDevice):
        raise APIBaseError(
            title='User already has an active TOTP device',
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


@router.post('/2fa/verify', response=TFAVerifyOut)
def verify_2fa(request, data: TFAVerifyIn):
    user_id = get_verification_context(data.id)
    user = get_object_or_404(User, id=user_id)

    # TODO: the device ID should be cached along with user ID in the verification context to avoid querying all devices.
    # For convenience, we use 'devices_for_user' to get the user's devices.
    device = list(devices_for_user(user=user))[-1]

    verify_cached_otp(device, user, data.purpose.value, data.passcode)

    if default_device(user) is None:
        device.name = 'default'
        device.save()

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=data.id)
    key_verif_user = VERIFICATION_USER_CACHE_KEY.format(id=user.id)

    cache.delete_many([key_verif_context, key_verif_user])

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@router.post('/password/forgot', response=MessageOut)
def forgot_password(request, data: ForgotPasswordIn):
    user = User.objects.filter(email=data.email).first() # Do not reveal if the email exists or not

    if user:
        token = default_token_generator.make_token(user)
        hashed = hashlib.sha256(token.encode('utf-8')).hexdigest()

        key_reset_password = RESET_TOKEN_CACHE_KEY.format(id=user.id)

        if cache.get(key_reset_password):
            # A reset token is already active for this user
            raise HttpError(429, 'A password reset link has already been sent recently. Please check your email.')

        cache.set(key_reset_password, hashed, RESET_TOKEN_WINDOW)

        context_id = set_verification_context(user)

        # For simplicity, we send the context ID and token directly in the email body.
        # In production, send these to the corresponding frontend link for password reset.
        reset_link = f'VERIFICATION CONTEXT: {context_id} \nTOKEN: {token}'

        send_mail(
            subject='Password reset request',
            message=f'Click the following link to reset your password: \n{reset_link}',
            from_email='no-reply@example.com',
            recipient_list=[user.email],
        )

    return {
        'message': 'If an account with that email exists, a password reset link has been sent.'
    }

@router.post('/password/reset', response=MessageOut)
def reset_password(request, data: ResetPasswordIn, purpose: UnAuthPurpose = UnAuthPurpose.RESET_PASSWORD):
    user_id = get_verification_context(data.id)
    user = get_object_or_404(User, id=user_id)
    device = default_device(user)

    # Verify the OTP passcode, do not clear the cached OTP data yet in case other verifications fail
    verify_cached_otp(device, user, purpose.value, data.passcode, clear=False)

    key_reset_password = RESET_TOKEN_CACHE_KEY.format(id=user.id)

    cached_token = cache.get(key_reset_password)
    hashed_token = hashlib.sha256(data.token.encode('utf-8')).hexdigest()

    if cached_token is None or cached_token != hashed_token:
        raise AuthenticationError()

    if not default_token_generator.check_token(user, data.token):
        raise AuthenticationError()

    user.set_password(data.new_password)
    user.save()

    # OTP cached values are only cleared after successful password reset
    key_hash = OTP_HASH_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=data.id)
    key_verif_user = VERIFICATION_USER_CACHE_KEY.format(id=user.id)

    # Clear the cache on successful verification
    cache.delete_many([key_hash, key_attempts, key_reset_password, key_verif_context, key_verif_user])

    return {
        'message': 'Password has been reset successfully'
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
def verify_old_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_OLD_PHONE):
    user: User = request.auth
    device = default_device(user)

    verify_cached_otp(device, user, purpose.value, data.passcode)

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    cache.set(key_phone_change, PHONE_CHANGE_OLD_VERIFIED, PHONE_CHANGE_WINDOW)

    return {
        'message': 'Old phone number verified'
    }

@router.post('/me/phone/change', response=MessageOut, auth=JWTAuth())
def change_phone(request, data: ChangePhoneIn, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    user: User = request.auth

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    if cache.get(key_phone_change) != PHONE_CHANGE_OLD_VERIFIED:
        raise HttpError(400, 'Old phone number not verified')

    temp_device = PhoneDevice(
        user=user,
        number=data.phone,
    )

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose.value, id=user.id)

    generate_cached_challenge(temp_device, key_hash, key_attempts)

    cache.set(key_phone_change, {
        'status': PHONE_CHANGE_NEW_AWAITING,
        'device_key': temp_device.key,
        'number': data.phone,
    }, PHONE_CHANGE_WINDOW)

    return {
        'message': 'OTP sent to new phone number'
    }



@router.post('/me/phone/verify-new', response=MessageOut, auth=JWTAuth())
def verify_new_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    user: User = request.auth
    device = default_device(user)

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(key_phone_change)

    if phone_change['status'] != PHONE_CHANGE_NEW_AWAITING:
        raise HttpError(400, 'New phone number change not initiated or old phone not verified')

    temp_device = PhoneDevice(
        key=phone_change['device_key'],
        user=user,
        number=phone_change['number'],
    )

    verify_cached_otp(temp_device, user, purpose.value, data.passcode)

    # Clear the phone change cache key after successful verification
    cache.delete(key_phone_change)

    user.phone = phone_change['number']
    device.number = phone_change['number']

    user.save()
    device.save()

    return {
        'message': 'New phone number verified, phone number updated'
    }
