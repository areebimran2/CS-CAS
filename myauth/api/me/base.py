from ninja import Router
from ninja_jwt.authentication import JWTAuth

from myauth.schemas import (
    UserProfileSchema, UserProfileUpdateSchema, MessageOut,
    SecuritySetupIn, VerifySchema,
    ChangePhoneIn, ChangePasswordIn, ChangeEmailIn, ChangeTFAMethodIn,
    AuthPurpose,
)
from myauth.services.profile import (
    get_profile, update_user_profile,
    send_secure_sms, verify_old_phone_number,
    initiate_phone_change, complete_phone_change,
    change_user_password, change_user_email, change_user_tfa_method,
)

router = Router(tags=['A2. My Profile'])


@router.get('', response=UserProfileSchema, auth=JWTAuth())
def profile(request):
    """
    Retrieve the authenticated user's profile information, including preferences.
    """
    return get_profile(request.auth)


@router.put('', response=UserProfileSchema, auth=JWTAuth())
def update_profile(request, data: UserProfileUpdateSchema):
    """
    Update the authenticated user's profile information, including preferences.
    """
    cleaned = data.model_dump(exclude_unset=True)
    return update_user_profile(request.auth, cleaned)


@router.post('/security/sms/send', response=MessageOut, auth=JWTAuth())
def secure_action(request, data: SecuritySetupIn):
    """
    Send an OTP SMS to the user's registered phone number for security-sensitive actions.
    """
    return send_secure_sms(request.auth, data.purpose.value)


@router.post('/phone/verify-old', response=MessageOut, auth=JWTAuth())
def verify_old_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_OLD_PHONE):
    """
    Verify the user's old phone number as stage 1 of the phone number change process.
    """
    return verify_old_phone_number(request.auth, data.passcode, purpose.value)


@router.post('/phone/change', response=MessageOut, auth=JWTAuth())
def change_phone(request, data: ChangePhoneIn, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    """
    Initiate stage 2 of the phone number change process by sending an OTP to the new phone number.
    """
    return initiate_phone_change(request.auth, data.phone, purpose.value)


@router.post('/phone/verify-new', response=MessageOut, auth=JWTAuth())
def verify_new_phone(request, data: VerifySchema, purpose: AuthPurpose = AuthPurpose.VERIFY_NEW_PHONE):
    """
    Verify the user's new phone number and update it in the system.
    """
    return complete_phone_change(request.auth, data.passcode, purpose.value)


@router.post('/password/change', response=MessageOut, auth=JWTAuth())
def password_change(request, data: ChangePasswordIn, purpose: AuthPurpose = AuthPurpose.CHANGE_PASSWORD):
    """
    Change the authenticated user's password after verifying the current password and OTP.
    """
    return change_user_password(request.auth, data.password, data.passcode, purpose.value)


@router.post('/email/change', response=MessageOut, auth=JWTAuth())
def email_change(request, data: ChangeEmailIn, purpose: AuthPurpose = AuthPurpose.CHANGE_EMAIL):
    """
    Change the authenticated user's email after verifying the OTP.
    """
    return change_user_email(request.auth, data.email, data.passcode, purpose.value)


@router.post('/tfa-method/change', response=MessageOut, auth=JWTAuth())
def tfa_method_change(request, data: ChangeTFAMethodIn, purpose: AuthPurpose = AuthPurpose.CHANGE_TFA_METHOD):
    """
    Change the authenticated user's two-factor authentication (TFA) method after verifying the OTP.
    """
    return change_user_tfa_method(request.auth, data.method, data.passcode, purpose.value)
