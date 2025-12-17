import hashlib
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_otp.plugins.otp_email.conf import settings
from ninja import Router
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.tokens import RefreshToken
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from common.utils import RESET_TOKEN_WINDOW, RESET_TOKEN_CACHE_KEY, VERIFICATION_USER_CACHE_KEY, \
    VERIFICATION_CONTEXT_CACHE_KEY, set_verification_context, get_context_or_session, validate_user_password, \
    set_user_session, set_refresh_cookie, SESSION_USER_CACHE_KEY
from myauth.schemas import *

router = Router(tags=['Session'])
User = get_user_model()


@router.post('/login', response=LoginOut)
def login(request, data: LoginIn):
    """
    Check if user credentials are valid and return user ID and 2FA method.

    If the user has not yet setup 2FA, then they must do so after this step by calling the appropriate 2FA setup
    endpoint (SMS default). Otherwise, they can proceed to verify 2FA using the returned method/device.


    		- Flow is as follows:
		  1. email+password+optional remember_me → `/api/auth/login` : gives back verification context id
		     - If a user has not established an auth device, setup SMS through `/api/auth/2fa/sms/send` or TOTP by calling `/api/auth/2fa/totp/setup` → `/api/auth/2fa/totp/confirm`
		  2. context id+purpose (login/reset) → `/api/auth/2fa/sms/send`: sends OTP
		  3. passcode+purpose (login/reset) → `/api/auth/2fa/verify`: establishes login session
    """
    user: Optional[User] = authenticate(username=data.email, password=data.password)
    if user is None:  # Invalid credentials
        raise APIBaseError(
            title='Invalid credentials',
            status=status.HTTP_401_UNAUTHORIZED,
            detail='Either email or password is invalid',
            errors=[{'field': 'email'}, {'field': 'password'}]
        )

    device = default_device(user)
    device_id = device.persistent_id if device else None

    context = {'device_id': device_id, 'remember_me': data.remember_me}
    context_id = set_verification_context(user, add_context=context)

    return {
        'id': context_id,
        'method': device
    }


@router.post('/logout', response=MessageOut)
def logout(request):
    """
    Should revoke refresh token that is stored in an HTTP-only cookie on the client side.

    Also, deny-list the access token to prevent its further use until it naturally expires.
    """
    cookie = request.COOKIES.get(settings.REFRESH_COOKIE_KEY)

    if not cookie:
        raise APIBaseError(
            title='Refresh token missing',
            detail='No refresh token cookie found in the request headers',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = RefreshToken(cookie)
    user = get_object_or_404(User, id=token['uid'])

    user_cache_key = SESSION_USER_CACHE_KEY.format(id=user.id)
    cache.delete(user_cache_key)

    resp = Response({
        'message': 'Logged out successfully'
    })

    resp.delete_cookie(settings.REFRESH_COOKIE_KEY)

    return resp


@router.post('/refresh', response=TokenOut)
def refresh(request):
    """
    Should issue a new access token using the refresh token stored in an HTTP-only cookie on the client side.

    Also, rotate the refresh token by issuing a new one and deny-list the access token.
    """
    cookie = request.COOKIES.get(settings.REFRESH_COOKIE_KEY)
    if not cookie:
        raise APIBaseError(
            title='Refresh token missing',
            detail='No refresh token cookie found in the request headers',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = RefreshToken(cookie)
    session = get_context_or_session(token['uid'])

    if not session:
        raise APIBaseError(
            title='Invalid refresh token',
            detail='No session data found for the user embedded in the given refresh token',
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if token['jti'] != session.get('jti') or token['sid'] != session.get('session_id'):
        # May want to log these events for security auditing
        message = 'old token reuse' if token['jti'] != session.get('jti') else 'old session attempt'
        raise APIBaseError(
            title='Invalid refresh token',
            detail='Refresh token does not match the stored session data: ' + message,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = get_object_or_404(User, id=token['uid'])
    new_token = RefreshToken.for_user(get_object_or_404(User, id=token['uid']))

    remaining_abs = max(0, token['exp'] - timezone.now().timestamp())
    new_token.set_exp(from_time=timezone.now(), lifetime=timedelta(seconds=remaining_abs)) # Keep the original expiry

    persistent = session.get('remember_me', False)

    set_user_session(user, new_token, persistent, old=token) # Keep the original session ID

    resp = Response({
        'access': str(new_token.access_token)
    })

    set_refresh_cookie(resp, new_token, persistent)

    return resp


@router.post('/password/forgot', response=MessageOut)
def forgot_password(request, data: ForgotPasswordIn):
    user = User.objects.filter(email=data.email).first()  # Do not reveal if the email exists or not

    if user:
        token = default_token_generator.make_token(user)
        hashed = hashlib.sha256(token.encode('utf-8')).hexdigest()

        key_reset_password = RESET_TOKEN_CACHE_KEY.format(id=user.id)

        if cache.get(key_reset_password):
            # A reset token is already active for this user
            raise APIBaseError(
                title='Password reset request error',
                detail='Password reset link has been sent recently. Please check the given email or try again later',
                status=status.HTTP_409_CONFLICT,
            )

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
def reset_password(request, data: ResetPasswordIn):
    context = get_context_or_session(data.id)
    user = get_object_or_404(User, id=context.get('user_id'))

    key_reset_password = RESET_TOKEN_CACHE_KEY.format(id=user.id)

    cached_tok = cache.get(key_reset_password)
    hashed_tok = hashlib.sha256(data.token.encode('utf-8')).hexdigest()

    if cached_tok is None or cached_tok != hashed_tok or not default_token_generator.check_token(user, data.token):
        raise APIBaseError(
            title='Password reset failed',
            detail='Error encountered when verifying password reset token',
            status=status.HTTP_401_UNAUTHORIZED,
            errors={'field': 'token', 'message': 'Invalid or expired token'},
        )

    validate_user_password(data.password, user=user)

    user.set_password(data.password)
    user.save()

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=data.id)
    key_verif_user = VERIFICATION_USER_CACHE_KEY.format(id=user.id)

    # Clear the cache on successful verification
    cache.delete_many([key_reset_password, key_verif_context, key_verif_user])

    return {
        'message': 'Password has been reset successfully'
    }
