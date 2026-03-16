import secrets
from typing import Optional

from django.core.cache import cache
from django.utils import timezone
from ninja.responses import Response
from ninja_jwt.tokens import Token

from myauth.models import User
from cs_cas import settings

# User logged-in session utilities
SESSION_USER_CACHE_KEY = 'session:user:{id}'
SESSION_IDLE_WINDOW = 7 * 24 * 3600  # For remembered sessions, idle timeout after 7 days
SESSION_TIMEOUT = 3600  # For non-remembered sessions, timed out after 1 hour of inactivity


def set_user_session(user: User, token: Token, remember_me: bool, old: Optional[Token] = None) -> None:
    """
    Creates or updates a logged-in session for the user.

    Note: It is assumed that if old is provided, it corresponds to an existing valid session that is to be updated.
          Otherwise, a new session is created. Additionally, the user ID claim in the old token must match the provided
          user ID.

    :param user: The User instance
    :param token: The authentication token (JWT)
    :param remember_me: Whether the user opted for a persistent session
    :param old: The old authentication token (JWT) if updating an existing session
    :return: None
    """
    if old:
        assert str(user.id) == old['uid'], 'Old token user ID does not match the provided user ID'
        session_id = old['sid']
    else:
        secure_id = secrets.token_urlsafe(16)  # Generate a secure identifier
        session_id = f'session.{secure_id}'

    # Keep track of the logged-in session state
    user_cache_key = SESSION_USER_CACHE_KEY.format(id=user.id)

    # TODO: If we want to support multiple sessions per user, do to following:
    #   1. Create a separate record for each session (e.g., SESSION_CACHE_KEY). This would map session_id to
    #      session data (user id, jti, remember_me, etc.)
    #   2. SESSION_USER_CACHE_KEY would be changed to maintain a set of active session IDs for the user (adds a lot of
    #      memory overhead, can bound # of sessions). Alternatively, we can maintain the "user version" and simply
    #      invalidate all sessions when the version is incremented (e.g., on password change).

    # For simplicity, we only track the latest session for the user
    context = {
        'session_id': session_id,
        'jti': token['jti'],
        'remember_me': remember_me,
    }

    remaining_abs = max(0, token['exp'] - timezone.now().timestamp())  # absolute remaining time of token validity

    # Store the session with appropriate timeout
    if remember_me:
        cache.set_many({user_cache_key: context}, remaining_abs)
    else:
        cache.set_many({user_cache_key: context}, min(SESSION_TIMEOUT, remaining_abs))

    token['uid'] = str(user.id)
    token['sid'] = session_id


def set_refresh_cookie(response: Response, token: Token, remember_me: bool) -> None:
    """
    Sets the refresh token in an HTTP-only cookie on the response.

    :param response: The Response instance
    :param token: The refresh Token instance
    :param remember_me: Whether the user opted for a persistent session
    :return: None
    """
    if remember_me:
        # maintain persistent session between browser restarts, but not beyond the token expiry
        remaining_abs = max(0, token['exp'] - timezone.now().timestamp())  # absolute remaining time of token validity
        max_age = max(0, min(remaining_abs, SESSION_IDLE_WINDOW) - 60)  # small expiry safety margin
    else:
        # session cookie, expires when client shuts down
        max_age = None

    response.set_cookie(
        key=settings.REFRESH_COOKIE_KEY,
        value=str(token),
        max_age=max_age,
        httponly=True,
        secure=not settings.DEBUG,
        # 'Strict' if on same domain, 'None' if cross-site
        samesite='Strict',
    )

