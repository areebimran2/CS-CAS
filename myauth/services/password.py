from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ninja_extra import status

from common.exceptions import APIBaseError
from myauth.models import User

# Forgot password utilities
RESET_TOKEN_CACHE_KEY = 'reset-token:{id}'
RESET_TOKEN_WINDOW = 900  # 15 minutes


def validate_user_password(password: str, user: User = None) -> None:
    """
    Validates the provided password. If a user is provided, it does so against the user's stored password.

    :param password: The password to validate
    :param user: The User instance for which this password is being set
    :return: None
    :raises APIBaseError: If the password does not meet the policy requirements
    """
    try:
        validate_password(password, user=user)
    except ValidationError as e:
        raise APIBaseError(
            title='Password validation error',
            detail='The provided new password does not meet the password policy requirements',
            status=status.HTTP_400_BAD_REQUEST,
            errors=[{'field': 'password', 'messages': e.messages}],
        )

