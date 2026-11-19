from ninja import Router

from common.access import authenticated
from common.schemas import MessageOut
from myauth.schemas import (
    AuthPurpose,
    ChangeEmailIn,
    ChangePasswordIn,
    ChangePhoneIn,
    ChangeTFAMethodIn,
    SecuritySetupIn,
    UserProfileSchema,
    UserProfileUpdateSchema,
    VerifySchema,
)
from myauth.services.profile import (
    change_user_email,
    change_user_password,
    change_user_tfa_method,
    complete_phone_change,
    get_profile,
    initiate_phone_change,
    send_secure_sms,
    update_user_profile,
    verify_old_phone_number,
)

router = Router(tags=['A2. My Profile'])


@router.get('', response=UserProfileSchema)
@authenticated
def get_my_profile(request):
    """
    Retrieve the authenticated user's profile information, including preferences.
    """
    return get_profile(request.auth)


@router.put('', response=UserProfileSchema)
@authenticated
def update_my_profile(request, data: UserProfileUpdateSchema):
    """
    Update the authenticated user's profile information, including preferences.
    """
    cleaned = data.model_dump(exclude_unset=True)
    return update_user_profile(request.auth, cleaned)


@router.post('/security/sms/send', response=MessageOut)
@authenticated
def send_security_sms(request, data: SecuritySetupIn):
    """
    Send an OTP SMS to the user's registered phone number for security-sensitive actions.
    """
    return send_secure_sms(request.auth, data.purpose.value)


@router.post('/phone/verify-old', response=MessageOut)
@authenticated
def verify_old_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_OLD_PHONE):
    """
    Verify the user's old phone number as stage 1 of the phone number change process.
    """
    return verify_old_phone_number(request.auth, data.passcode, purpose.value)


@router.post('/phone/change', response=MessageOut)
@authenticated
def change_phone(request, data: ChangePhoneIn, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    """
    Initiate stage 2 of the phone number change process by sending an OTP to the new phone number.
    """
    return initiate_phone_change(request.auth, data.phone, purpose.value)


@router.post('/phone/verify-new', response=MessageOut)
@authenticated
def verify_new_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    """
    Verify the user's new phone number and update it in the system.
    """
    return complete_phone_change(request.auth, data.passcode, purpose.value)


@router.post('/password/change', response=MessageOut)
@authenticated
def change_password(request, data: ChangePasswordIn, purpose: AuthPurpose = AuthPurpose.CHANGE_PASSWORD):
    """
    Change the authenticated user's password after verifying the current password and OTP.
    """
    return change_user_password(request.auth, data.password, data.passcode, purpose.value)


@router.post('/email/change', response=MessageOut)
@authenticated
def change_email(request, data: ChangeEmailIn, purpose: AuthPurpose = AuthPurpose.CHANGE_EMAIL):
    """
    Change the authenticated user's email after verifying the OTP.
    """
    return change_user_email(request.auth, data.email, data.passcode, purpose.value)


@router.post('/tfa-method/change', response=MessageOut)
@authenticated
def change_tfa_method(request, data: ChangeTFAMethodIn, purpose: AuthPurpose = AuthPurpose.CHANGE_TFA_METHOD):
    """
    Change the authenticated user's two-factor authentication (TFA) method after verifying the OTP.
    """
    return change_user_tfa_method(request.auth, data.method, data.passcode, purpose.value)
