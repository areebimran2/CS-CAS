import hashlib
from datetime import timedelta
from typing import Optional, Dict, Tuple, Any

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.tokens import RefreshToken
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from cs_cas import settings
from myauth.services.password import validate_user_password, RESET_TOKEN_CACHE_KEY, RESET_TOKEN_WINDOW
from myauth.services.session import set_user_session, set_refresh_cookie, SESSION_USER_CACHE_KEY
from myauth.services.verification import (
    set_verification_context, get_context_or_session,
    VERIFICATION_USER_CACHE_KEY, VERIFICATION_CONTEXT_CACHE_KEY,
)

User = get_user_model()


def authenticate_user(email: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
    """
    Validates user credentials and creates a verification context for subsequent 2FA.

    :param email: The user's email
    :param password: The user's password
    :param remember_me: Whether the user opted for a persistent session
    :return: dict with 'id' (context_id) and 'method' (device or None)
    """
    user: Optional[User] = authenticate(username=email, password=password)
    if user is None:  # Invalid credentials
        raise APIBaseError(
            title='Invalid credentials',
            status=status.HTTP_401_UNAUTHORIZED,
            detail='Either email or password is invalid',
            errors=[{'field': 'email'}, {'field': 'password'}]
        )

    device = default_device(user)
    device_id = device.persistent_id if device else None

    context = {'device_id': device_id, 'remember_me': remember_me}
    context_id = set_verification_context(user, add_context=context)

    return {
        'id': context_id,
        'method': device
    }


def logout_user(cookie: Optional[str]) -> Response:
    """
    Destroys the user session and clears the refresh token cookie.

    :param cookie: The refresh token cookie value (may be None)
    :return: Response with cookie deleted
    """
    if cookie:
        token = RefreshToken(cookie)
        user = get_object_or_404(User, id=token['uid'])

        user_cache_key = SESSION_USER_CACHE_KEY.format(id=user.id)
        cache.delete(user_cache_key)

    resp = Response({
        'message': 'Logged-in session has been cleared successfully.'
    })

    resp.delete_cookie(settings.REFRESH_COOKIE_KEY)

    return resp


def refresh_session(cookie: Optional[str]) -> Response:
    """
    Rotates the refresh token and returns a new access token.

    :param cookie: The refresh token cookie value
    :return: Response with new access token and rotated refresh cookie
    """
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


def initiate_password_reset(email: str) -> Dict[str, str]:
    """
    Sends a password reset email if the account exists.

    :param email: The user's email address
    :return: dict with a generic message (does not reveal existence)
    """
    user = User.objects.filter(email=email).first()  # Do not reveal if the email exists or not

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


def complete_password_reset(context_id: str, token: str, password: str) -> Dict[str, str]:
    """
    Verifies the reset token and sets a new password.

    :param context_id: The verification context ID
    :param token: The password reset token
    :param password: The new password
    :return: dict with success message
    """
    context = get_context_or_session(context_id)
    user = get_object_or_404(User, id=context.get('user_id'))

    key_reset_password = RESET_TOKEN_CACHE_KEY.format(id=user.id)

    cached_tok = cache.get(key_reset_password)
    hashed_tok = hashlib.sha256(token.encode('utf-8')).hexdigest()

    if cached_tok is None or cached_tok != hashed_tok or not default_token_generator.check_token(user, token):
        raise APIBaseError(
            title='Password reset failed',
            detail='Error encountered when verifying password reset token',
            status=status.HTTP_401_UNAUTHORIZED,
            errors={'field': 'token', 'message': 'Invalid or expired token'},
        )

    validate_user_password(password, user=user)

    user.set_password(password)
    user.save()

    # Clear the verification session
    key_verif_context = VERIFICATION_CONTEXT_CACHE_KEY.format(id=context_id)
    key_verif_user = VERIFICATION_USER_CACHE_KEY.format(id=user.id)

    # Clear the cache on successful verification
    cache.delete_many([key_reset_password, key_verif_context, key_verif_user])

    return {
        'message': 'Password has been reset successfully'
    }

