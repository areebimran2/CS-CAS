from django.core.cache import cache
from ninja import Router, PatchDict
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from common.utils import generate_cached_challenge, OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, \
    verify_cached_otp, PHONE_CHANGE_CACHE_KEY, PHONE_CHANGE_WINDOW, PHONE_CHANGE_OLD_VERIFIED, \
    PHONE_CHANGE_NEW_AWAITING, validate_new_password
from myauth.schemas import *

router = Router(tags=['Session'])
User = get_user_model()


@router.get('', response=UserSchema, auth=JWTAuth())
def profile(request):
    user: User = request.auth
    return user


@router.put('', response=UserSchema, auth=JWTAuth())
def update_profile(request, data: PatchDict[UserBasicUpdateSchema]):
    user: User = request.auth

    for attr, value in data.items():
        setattr(user, attr, value)

    user.save()

    return user


@router.post('/security/sms/send', response=MessageOut, auth=JWTAuth())
def secure_action(request, data: SecuritySetupIn):
    user: User = request.auth
    device = default_device(user)  # Assume that every user has SMS 2FA enabled

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)

    # Send the OTP SMS to the user's phone
    generate_cached_challenge(device, key_hash, key_attempts)

    return {
        'message': 'SMS sent to registered phone number'
    }


@router.post('/phone/verify-old', response=MessageOut, auth=JWTAuth())
def verify_old_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_OLD_PHONE):
    user: User = request.auth
    device = default_device(user)

    verify_cached_otp(device, user, purpose.value, data.passcode)

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    cache.set(key_phone_change, {'status': PHONE_CHANGE_OLD_VERIFIED}, PHONE_CHANGE_WINDOW)

    return {
        'message': 'Old phone number verified'
    }


@router.post('/phone/change', response=MessageOut, auth=JWTAuth())
def change_phone(request, data: ChangePhoneIn, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    user: User = request.auth

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(key_phone_change)
    if phone_change.get('status') != PHONE_CHANGE_OLD_VERIFIED:
        raise APIBaseError(
            title='Error in phone number change flow',
            detail='Old phone number not verified',
            status=status.HTTP_400_BAD_REQUEST,
        )

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


@router.post('/phone/verify-new', response=MessageOut, auth=JWTAuth())
def verify_new_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    user: User = request.auth
    device = default_device(user)

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(key_phone_change)

    if phone_change.get('status') != PHONE_CHANGE_NEW_AWAITING:
        raise APIBaseError(
            title='Error in phone number change flow',
            detail='New phone number change not initiated or old phone not verified',
            status=status.HTTP_400_BAD_REQUEST,
        )

    temp_device = PhoneDevice(
        key=phone_change.get('device_key'),
        user=user,
        number=phone_change.get('number'),
    )

    verify_cached_otp(temp_device, user, purpose.value, data.passcode)

    # Clear the phone change cache key after successful verification
    cache.delete(key_phone_change)

    user.phone = phone_change.get('number')
    device.number = phone_change.get('number')

    user.save()
    device.save()

    return {
        'message': 'New phone number verified, phone number updated'
    }


@router.post('/password/change', response=MessageOut, auth=JWTAuth())
def password_change(request, data: ChangePasswordIn, purpose: AuthPurpose = AuthPurpose.CHANGE_PASSWORD):
    user: User = request.auth
    validate_new_password(user, data.new_password)

    device = default_device(user)
    verify_cached_otp(device, user, purpose.value, data.passcode)

    user.set_password(data.new_password)
    user.save()

    return {
        'message': 'Password changed successfully'
    }


@router.post('/email/change', response=MessageOut, auth=JWTAuth())
def email_change(request, data: ChangeEmailIn, purpose: AuthPurpose = AuthPurpose.CHANGE_EMAIL):
    user: User = request.auth
    device = default_device(user)

    verify_cached_otp(device, user, purpose.value, data.passcode)

    user.email = data.email
    user.save()

    return {
        'message': 'Email changed successfully'
    }


@router.post('/2fa-method/change', response=MessageOut, auth=JWTAuth())
def tfa_method_change(request, data: ChangeTFAMethodIn, purpose: AuthPurpose = AuthPurpose.CHANGE_TFA_METHOD):
    # This implementation is unfinished, and requires further checks to ensure proper TFA setup.
    # TODO: Need to re-setup TFA after changing method
    user: User = request.auth
    device = default_device(user)

    verify_cached_otp(device, user, purpose.value, data.passcode)

    device.delete()  # Remove existing 2FA device

    user.twofa_method = data.method
    user.save()

    return {
        'message': 'TFA method changed successfully'
    }
