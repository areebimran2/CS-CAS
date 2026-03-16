from typing import Dict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from ninja_extra import status
from phonenumber_field.phonenumber import PhoneNumber as PhoneNumberObj
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from myauth.models import UserPreference
from myauth.services.otp import OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, generate_cached_code, verify_cached_code
from myauth.services.password import validate_user_password
from myauth.services.verification import (
    PHONE_CHANGE_CACHE_KEY, PHONE_CHANGE_WINDOW,
    PHONE_CHANGE_OLD_VERIFIED, PHONE_CHANGE_NEW_AWAITING,
)

User = get_user_model()


def get_profile(user):
    """
    Retrieve the user profile, ensuring preferences exist.

    :param user: The authenticated User instance
    :return: The user instance (with preferences guaranteed)
    """
    # Ensure user preferences exist (safety check), potentially remove later
    if getattr(user, 'preferences', None) is None:
        setattr(user, 'preferences', UserPreference.objects.create(user=user))

    return user


def update_user_profile(user, cleaned_data: Dict):
    """
    Update user fields and preferences from cleaned data.

    :param user: The authenticated User instance
    :param cleaned_data: dict of fields to update (may include 'preferences' key)
    :return: The updated user instance
    """
    # Ensure user preferences exist (safety check), potentially remove later
    if getattr(user, 'preferences', None) is None:
        setattr(user, 'preferences', UserPreference.objects.create(user=user))

    user_prefs: UserPreference = user.preferences

    prefs = cleaned_data.pop('preferences', {})

    # Update basic user fields
    for field in cleaned_data:
        setattr(user, field, cleaned_data[field])

    # Update user preferences
    for pref in prefs:
        setattr(user_prefs, pref, prefs[pref])

    user_prefs.save()
    user.save()

    return user


def send_secure_sms(user, purpose_value: str) -> Dict[str, str]:
    """
    Send an OTP SMS for a security-sensitive action.

    :param user: The authenticated User instance
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose_value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose_value, id=user.id)

    # Send the OTP SMS to the user's phone
    generate_cached_code(user.phone, key_hash, key_attempts)

    return {
        'message': 'SMS sent to registered phone number'
    }


def verify_old_phone_number(user, passcode: str, purpose_value: str) -> Dict[str, str]:
    """
    Verify the user's old phone number (stage 1 of phone change).

    :param user: The authenticated User instance
    :param passcode: The OTP passcode
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    verify_cached_code(user, purpose_value, passcode)

    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    cache.set(key_phone_change, {'status': PHONE_CHANGE_OLD_VERIFIED}, PHONE_CHANGE_WINDOW)

    return {
        'message': 'Old phone number verified'
    }


def initiate_phone_change(user, new_phone: str, purpose_value: str) -> Dict[str, str]:
    """
    Initiate stage 2 of phone change — send OTP to the new number.

    :param user: The authenticated User instance
    :param new_phone: The new phone number string
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(key_phone_change)
    if phone_change.get('status') != PHONE_CHANGE_OLD_VERIFIED:
        raise APIBaseError(
            title='Error in phone number change flow',
            detail='Old phone number not verified',
            status=status.HTTP_400_BAD_REQUEST,
        )

    key_hash = OTP_HASH_CACHE_KEY.format(purpose=purpose_value, id=user.id)
    key_attempts = OTP_ATTEMPT_CACHE_KEY.format(purpose=purpose_value, id=user.id)

    generate_cached_code(PhoneNumberObj.from_string(new_phone), key_hash, key_attempts)

    cache.set(key_phone_change, {
        'status': PHONE_CHANGE_NEW_AWAITING,
        'number': new_phone,
    }, PHONE_CHANGE_WINDOW)

    return {
        'message': 'OTP sent to new phone number'
    }


def complete_phone_change(user, passcode: str, purpose_value: str) -> Dict[str, str]:
    """
    Verify the new phone number and update it (stage 3 of phone change).

    :param user: The authenticated User instance
    :param passcode: The OTP passcode
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    key_phone_change = PHONE_CHANGE_CACHE_KEY.format(id=user.id)
    phone_change = cache.get(key_phone_change)

    if phone_change.get('status') != PHONE_CHANGE_NEW_AWAITING:
        raise APIBaseError(
            title='Error in phone number change flow',
            detail='New phone number change not initiated or old phone not verified',
            status=status.HTTP_400_BAD_REQUEST,
        )

    verify_cached_code(user, purpose_value, passcode)

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


def change_user_password(user, password: str, passcode: str, purpose_value: str) -> Dict[str, str]:
    """
    Change the user's password after OTP verification.

    :param user: The authenticated User instance
    :param password: The new password
    :param passcode: The OTP passcode
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    validate_user_password(password, user=user)

    verify_cached_code(user, purpose_value, passcode)

    user.set_password(password)
    user.save()

    return {
        'message': 'Password changed successfully'
    }


def change_user_email(user, email: str, passcode: str, purpose_value: str) -> Dict[str, str]:
    """
    Change the user's email after OTP verification.

    :param user: The authenticated User instance
    :param email: The new email address
    :param passcode: The OTP passcode
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    verify_cached_code(user, purpose_value, passcode)

    user.email = email
    user.save()

    return {
        'message': 'Email changed successfully'
    }


def change_user_tfa_method(user, method: str, passcode: str, purpose_value: str) -> Dict[str, str]:
    """
    Change the user's TFA method after OTP verification.

    :param user: The authenticated User instance
    :param method: The new TFA method
    :param passcode: The OTP passcode
    :param purpose_value: The purpose string value
    :return: dict with message
    """
    # This implementation is unfinished, and requires further checks to ensure proper TFA setup.
    # TODO: Need to re-setup TFA after changing method
    device = default_device(user)

    verify_cached_code(user, purpose_value, passcode)

    device.delete()  # Remove existing 2FA device

    user.twofa_method = method
    user.save()

    return {
        'message': 'TFA method changed successfully'
    }

