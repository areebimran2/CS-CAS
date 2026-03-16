from ninja import Router

from cs_cas import settings
from myauth.schemas import (
    LoginIn, LoginOut, TokenOut, MessageOut,
    ForgotPasswordIn, ResetPasswordIn,
)
from myauth.services.auth import (
    authenticate_user, logout_user, refresh_session,
    initiate_password_reset, complete_password_reset,
)

router = Router(tags=['A1. Login / 2FA / Forgotten Password'])


@router.post('/login', response=LoginOut)
def login(request, data: LoginIn):
    """
    Check if the given user credentials are valid, then establish a login verification context. The context ID along
    with the user's default 2FA method/device (if any) are returned.

    If the user has not yet setup 2FA, then they must do so after this step by calling the appropriate 2FA setup
    endpoint (SMS default). Otherwise, they can proceed to verify 2FA using the returned method/device.

    SMS: OTP is sent through `/api/auth/2fa/sms/send` endpoint.
    TOTP: OTP is generated through authenticator apps (e.g Google Authenticator).

    **Note**: This endpoint does NOT establish a login session. The session is only created after successful
    2FA verification.
    """
    return authenticate_user(data.email, data.password, data.remember_me)


@router.post('/logout', response=MessageOut)
def logout(request):
    """
    Logout the user by deleting their session and refresh token cookie.
    """
    cookie = request.COOKIES.get(settings.REFRESH_COOKIE_KEY)
    return logout_user(cookie)


@router.post('/refresh', response=TokenOut)
def refresh(request):
    """
    Refresh the access token using a valid refresh token from cookies.
    """
    cookie = request.COOKIES.get(settings.REFRESH_COOKIE_KEY)
    return refresh_session(cookie)


@router.post('/password/forgot', response=MessageOut)
def forgot_password(request, data: ForgotPasswordIn):
    """
    Initiate the password reset process by sending a reset link to the user's email.
    """
    return initiate_password_reset(data.email)


@router.post('/password/reset', response=MessageOut)
def reset_password(request, data: ResetPasswordIn):
    """
    Complete the password reset process by verifying the token and setting a new password.
    """
    return complete_password_reset(data.id, data.token, data.password)
