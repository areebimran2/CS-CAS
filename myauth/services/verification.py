import secrets
from typing import Optional, Dict, Any

from django.core.cache import cache
from ninja_extra import status

from common.exceptions import APIBaseError
from myauth.models import User

# User verification context utilities
VERIFICATION_CONTEXT_CACHE_KEY = 'verification:context:{id}'
VERIFICATION_USER_CACHE_KEY = 'verification:user:{id}'
VERIFICATION_WINDOW = 600  # 10 minutes

# Phone change utilities
PHONE_CHANGE_CACHE_KEY = 'phone-change:{id}'
PHONE_CHANGE_OLD_VERIFIED = 'old-verified'
PHONE_CHANGE_NEW_AWAITING = 'new-awaiting-verification'
PHONE_CHANGE_WINDOW = 300  # 5 minutes

# Session cache key (imported here for get_context_or_session lookup)
from myauth.services.session import SESSION_USER_CACHE_KEY


def set_verification_context(user: User, add_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Initializes a verification context for the user and returns the context ID. The context is typically just the user
    ID, but additional context information can be added as needed.

    :param user: The User instance
    :param add_context: Additional Context information to store (e.g., device_id, remember_me)
    :return: The verification context ID
    """
    token = secrets.token_urlsafe(16)  # Generate a secure identifier to send to the client
    verif_id = f'verif.{token}'

    # Keep track of the verification context in the cache, the user id is mapped back to the token to ensure the
    # user has only one active verification session at a time.
    context_cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=verif_id)  # Link the token to the user ID
    user_cache_key = VERIFICATION_USER_CACHE_KEY.format(id=user.id)  # Link the user ID to the token

    # Check for existing verification context
    existing_cache_id = cache.get(user_cache_key)
    existing_cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=existing_cache_id) if existing_cache_id else None

    # Invalidate any existing verification context for the user
    cache.delete_many([existing_cache_key])

    context = {'user_id': user.id}

    if add_context:
        context |= add_context

    cache.set_many({context_cache_key: context, user_cache_key: verif_id}, VERIFICATION_WINDOW)

    return verif_id


def get_context_or_session(cache_id: str) -> Dict[str, Any]:
    """
    Helper function to retrieve either a verification context or user session based on the cache key pattern.

    :param cache_id: The cache key ID (either verification context ID or user ID for session)
    :return: The retrieved context or session information
    :raises APIBaseError: If the context or session is invalid or expired
    """
    if cache_id.startswith('verif'):
        cache_key = VERIFICATION_CONTEXT_CACHE_KEY.format(id=cache_id)
        err_message = 'The client has not established a valid verification context for a user, or it has expired.'
    else:
        cache_key = SESSION_USER_CACHE_KEY.format(id=cache_id)
        err_message = 'The client has not established a valid session for the given user, or it has expired.'

    data = cache.get(cache_key)

    if data is None:
        raise APIBaseError(
            title='User verification context or session error',
            detail=err_message,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return data

