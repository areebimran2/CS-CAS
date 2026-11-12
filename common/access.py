"""
Access control for API endpoints.

Every endpoint must declare who may call it, with one of these decorators placed directly under the route decorator:

    @router.get('/{ship_id}', response=ShipOut)
    @requires('ships.view')          # signed in, with this permission (all of them, if several are given)
    def get_ship(request, ship_id): ...

    @authenticated                   # signed in, any permissions (e.g. the user's own profile)
    @public                          # no sign-in at all (e.g. login)

An endpoint without a declaration is refused for everyone.

Signed in means the request carries a valid access token: `Authorization: Bearer <token>`.
"""
from django.core.exceptions import ImproperlyConfigured
from ninja.utils import contribute_operation_callback
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import AuthenticationFailed

from common.exceptions import NotAuthenticatedError, PermissionDeniedError
from common.permissions import PERMISSIONS


class BearerAuth(JWTAuth):
    """
    Accepts a valid access token for an active user who has all of the given permissions. With no permissions given,
    any signed-in user is accepted. Superusers have every permission.
    """

    def __init__(self, *permissions: str):
        super().__init__()
        self.permissions = frozenset(permissions)

    def authenticate(self, request, token):
        try:
            user = super().authenticate(request, token)
        except AuthenticationFailed as exc:  # bad or expired token, or a suspended user
            raise NotAuthenticatedError(detail=str(exc.detail.get('detail', exc.detail)))

        missing = {perm for perm in self.permissions if not user.has_perm(perm)}
        if missing:
            raise PermissionDeniedError(detail=f"Requires the permission(s): {', '.join(sorted(missing))}")
        return user


class DenyUndeclared(BearerAuth):
    """The API-wide default. Refuses every request to an endpoint that hasn't declared who may call it."""

    def authenticate(self, request, token):
        super().authenticate(request, token)  # anonymous callers still get 401, signed-in callers 403
        raise PermissionDeniedError(detail='This endpoint does not declare who may use it.')


def public(view_func):
    """Allow anyone, signed in or not."""
    return _set_access(view_func, None)


def authenticated(view_func):
    """Allow any signed-in user."""
    return _set_access(view_func, BearerAuth())


def requires(*permissions: str):
    """Allow signed-in users who have every one of the given permissions."""
    unknown = set(permissions) - PERMISSIONS.keys()
    if not permissions or unknown:
        raise ImproperlyConfigured(f'@requires needs permissions from common/permissions.py, got: {permissions}')

    def decorator(view_func):
        return _set_access(view_func, BearerAuth(*permissions), note=f"**Permission:** `{'`, `'.join(permissions)}`")
    return decorator


def _set_access(view_func, auth, note=None):
    """
    Set the endpoint's auth when ninja builds its operation. This uses ninja's hook for decorators (the same one as
    ninja.decorators.decorate_view), which is why the decorator must sit below the route decorator. An operation with
    its own auth is not given the API-wide default.
    """
    def apply(operation):
        operation.auth_param = auth
        operation.auth_callbacks = [auth] if auth else []
        if note:  # show the required permission in the API docs
            operation.description = f'{operation.description}\n\n{note}'.strip()

    contribute_operation_callback(view_func, apply)
    return view_func
