from django.core.cache import cache
from phonenumber_field.phonenumber import PhoneNumber as PhoneNumberObj
from ninja import Router
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from common.utils import OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, \
    PHONE_CHANGE_CACHE_KEY, PHONE_CHANGE_WINDOW, PHONE_CHANGE_OLD_VERIFIED, \
    PHONE_CHANGE_NEW_AWAITING, validate_new_password, generate_cached_code, verify_cached_code
from myauth.schemas import *

router = Router(tags=['Session'])
User = get_user_model()


@router.get('', response=UserProfileSchema, auth=JWTAuth())
def profile(request):
    user: User = request.auth # Assume that every user has preferences

    # Ensure user preferences exist (safety check), potentially remove later
    if getattr(user, 'preferences', None) is None:
        setattr(user, 'preferences', UserPreference.objects.create(user=user))

    return user


@router.put('', response=UserProfileSchema, auth=JWTAuth())
def update_profile(request, data: UserProfileUpdateSchema):
    user: User = request.auth

    # Ensure user preferences exist (safety check), potentially remove later
    if getattr(user, 'preferences', None) is None:
        setattr(user, 'preferences', UserPreference.objects.create(user=user))

    user_prefs: UserPreference = user.preferences

    cleaned = data.model_dump(exclude_unset=True)
    prefs = cleaned.pop('prefs', {})

    # Update basic user fields
    for field in cleaned:
        setattr(user, field, cleaned[field])

    # Update user preferences
    for pref in prefs:
        setattr(user_prefs, pref, prefs[pref])

    user_prefs.save()
    user.save()

    return user


@router.post('/security/sms/send', response=MessageOut, auth=JWTAuth())
def secure_action(request, data: SecuritySetupIn):
    user: User = request.auth

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=data.purpose.value, id=user.id)

    # Send the OTP SMS to the user's phone
    generate_cached_code(user.phone, key_hash, key_attempts)

    return {
        'message': 'SMS sent to registered phone number'
    }


@router.post('/phone/verify-old', response=MessageOut, auth=JWTAuth())
def verify_old_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_OLD_PHONE):
    user: User = request.auth

    verify_cached_code(user, purpose.value, data.passcode)

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

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose.value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose.value, id=user.id)

    generate_cached_code(PhoneNumberObj.from_string(data.phone), key_hash, key_attempts)

    cache.set(key_phone_change, {
        'status': PHONE_CHANGE_NEW_AWAITING,
        'number': data.phone,
    }, PHONE_CHANGE_WINDOW)

    return {
        'message': 'OTP sent to new phone number'
    }


@router.post('/phone/verify-new', response=MessageOut, auth=JWTAuth())
def verify_new_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    user: User = request.auth

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(key_phone_change)

    if phone_change.get('status') != PHONE_CHANGE_NEW_AWAITING:
        raise APIBaseError(
            title='Error in phone number change flow',
            detail='New phone number change not initiated or old phone not verified',
            status=status.HTTP_400_BAD_REQUEST,
        )

    verify_cached_code(user, purpose.value, data.passcode)

    # Clear the phone change cache key after successful verification
    cache.delete(key_phone_change)

    device = PhoneDevice.objects.filter(user=user, number=user.phone).first()

    user.phone = phone_change.get('number')
    user.save()

    if device:
        device.number = phone_change.get('number')
        device.save()

    return {
        'message': 'New phone number verified, phone number updated'
    }


@router.post('/password/change', response=MessageOut, auth=JWTAuth())
def password_change(request, data: ChangePasswordIn, purpose: AuthPurpose = AuthPurpose.CHANGE_PASSWORD):
    user: User = request.auth
    validate_new_password(user, data.new_password)

    verify_cached_code(user, purpose.value, data.passcode)

    user.set_password(data.new_password)
    user.save()

    return {
        'message': 'Password changed successfully'
    }


@router.post('/email/change', response=MessageOut, auth=JWTAuth())
def email_change(request, data: ChangeEmailIn, purpose: AuthPurpose = AuthPurpose.CHANGE_EMAIL):
    user: User = request.auth

    verify_cached_code(user, purpose.value, data.passcode)

    user.email = data.email
    user.save()

    return {
        'message': 'Email changed successfully'
    }


@router.post('/tfa-method/change', response=MessageOut, auth=JWTAuth())
def tfa_method_change(request, data: ChangeTFAMethodIn, purpose: AuthPurpose = AuthPurpose.CHANGE_TFA_METHOD):
    # This implementation is unfinished, and requires further checks to ensure proper TFA setup.
    # TODO: Need to re-setup TFA after changing method
    user: User = request.auth
    device = default_device(user)

    verify_cached_code(user, purpose.value, data.passcode)

    device.delete()  # Remove existing 2FA device

    user.twofa_method = data.method
    user.save()

    return {
        'message': 'TFA method changed successfully'
    }
