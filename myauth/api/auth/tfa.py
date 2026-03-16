from ninja import Router

from myauth.schemas import (
    TFASetupTOTPIn, TFASetupTOTPOut,
    TFAConfirmTOTPIn, TFAConfirmOut,
    TFASetupSMSIn, TFAVerifyIn,
    TFAMethod, UnAuthPurpose, TokenOut,
)
from myauth.services.tfa import (
    setup_totp, confirm_totp, send_sms_otp, verify_2fa_and_create_session,
)

router = Router(tags=['A1. Login / 2FA / Forgotten Password'])


@router.post('/totp/setup', response=TFASetupTOTPOut)
def setup_tfa_totp(request, data: TFASetupTOTPIn):
    """
    Initiate TOTP 2FA setup for the user by generating a TOTP secret and OTP URI.

    The OTP URI should be used to generate a QR code for the user to scan with their authenticator app.
    """
    return setup_totp(data.id, TFAMethod.TOTP)


@router.post('/totp/confirm', response=TFAConfirmOut)
def confirm_tfa_totp(request, data: TFAConfirmTOTPIn):
    """
    Confirm TOTP 2FA setup by verifying the provided passcode against the TOTP secret.
    """
    return confirm_totp(data.id, data.url, data.passcode)


@router.post('/sms/send', response=TFAConfirmOut)
def send_2fa_sms(request, data: TFASetupSMSIn, purpose: UnAuthPurpose = UnAuthPurpose.LOGIN):
    """
    Send an OTP SMS to the user's registered phone number for SMS 2FA verification.
    """
    return send_sms_otp(data.id, purpose.value, TFAMethod.SMS)


@router.post('/verify', response=TokenOut)
def verify_2fa(request, data: TFAVerifyIn, purpose: UnAuthPurpose = UnAuthPurpose.LOGIN):
    """
    Verify the provided 2FA passcode and establish a user session upon successful verification.
    """
    return verify_2fa_and_create_session(data.id, data.passcode, purpose.value, TFAMethod.SMS)
