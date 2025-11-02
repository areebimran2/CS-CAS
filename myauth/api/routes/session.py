import hashlib

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_extra import status
from two_factor.utils import default_device

from common.exceptions import APIBaseError
from common.utils import OTP_HASH_CACHE_KEY, OTP_ATTEMPT_CACHE_KEY, \
    verify_cached_otp, RESET_TOKEN_WINDOW, RESET_TOKEN_CACHE_KEY, VERIFICATION_USER_CACHE_KEY, \
    VERIFICATION_CONTEXT_CACHE_KEY, set_verification_context, get_verification_context, validate_new_password
from myauth.api.schemas import *

router = Router(tags=['Session'])
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

@router.post('/password/forgot', response=MessageOut)
def forgot_password(request, data: ForgotPasswordIn):
    user = User.objects.filter(email=data.email).first() # Do not reveal if the email exists or not

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
def reset_password(request, data: ResetPasswordIn, purpose: UnAuthPurpose = UnAuthPurpose.RESET_PASSWORD):
    user_id = get_verification_context(data.id)
    user = get_object_or_404(User, id=user_id)
    device = default_device(user)

    # Verify the OTP passcode, do not clear the cached OTP data yet in case other verifications fail
    verify_cached_otp(device, user, purpose.value, data.passcode, clear=False)

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

    validate_new_password(user, data.new_password)

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