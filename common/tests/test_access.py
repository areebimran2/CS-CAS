"""
Tests for API access control (common/access.py): every endpoint declares who may use it, and the rules are enforced.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from ninja_jwt.tokens import AccessToken

from common.access import requires
from common.permissions import PERMISSIONS
from cs_cas.api import api
from myadmin.models import Permission, Role

SHIPS_URL = '/api/ships/'  # GET requires ships.view
PROFILE_URL = '/api/me/'   # any signed-in user


def test_every_endpoint_declares_who_may_use_it():
    """Endpoints without @public, @authenticated or @requires(...) fall back to DenyUndeclared."""
    undeclared = [
        f'{method.upper()} {path}'
        for path, operations in api.get_openapi_schema()['paths'].items()
        for method, operation in operations.items()
        if any('DenyUndeclared' in rule for rule in operation.get('security', []))
    ]
    assert undeclared == [], 'Add @public, @authenticated or @requires(...) to these endpoints'


def test_requires_rejects_permissions_missing_from_the_catalogue():
    with pytest.raises(ImproperlyConfigured):
        requires('ships.edti')


@pytest.mark.django_db
def test_migrate_copies_the_catalogue_into_the_permissions_table():
    assert set(Permission.objects.values_list('key', flat=True)) >= PERMISSIONS.keys()


# -- Enforcement, using GET /api/ships/ (requires ships.view)

@pytest.fixture
def make_user(db):
    """Creates users with no roles. Phone numbers must be unique, so each user gets the next one."""
    phones = (f'+4477009001{n:02d}' for n in range(100))

    def make(email, **fields):
        return get_user_model().objects.create_user(
            email=email, password='correct-horse-battery-staple', first_name='Test', last_name='User',
            phone=next(phones), **fields,
        )
    return make


def bearer(user):
    return {'HTTP_AUTHORIZATION': f'Bearer {AccessToken.for_user(user)}'}


def grant(user, *keys):
    role = Role.objects.create(name=f'Role for {user.email}')
    role.permissions.set(Permission.objects.filter(key__in=keys))
    role.users.add(user)


def test_no_token_is_401(client, db):
    response = client.get(SHIPS_URL)

    assert response.status_code == 401
    assert response.json()['type'] == 'NOT_AUTHENTICATED'


def test_invalid_token_is_401(client, db):
    response = client.get(SHIPS_URL, HTTP_AUTHORIZATION='Bearer not-a-real-token')

    assert response.status_code == 401
    assert response.json()['type'] == 'NOT_AUTHENTICATED'


def test_suspended_user_is_401(client, make_user):
    user = make_user(email='suspended@example.com', status='suspended')

    assert client.get(SHIPS_URL, **bearer(user)).status_code == 401


def test_signed_in_without_the_permission_is_403(client, make_user):
    user = make_user(email='no-perms@example.com')

    response = client.get(SHIPS_URL, **bearer(user))

    assert response.status_code == 403
    assert response.json()['type'] == 'PERMISSION_DENIED'
    assert 'ships.view' in response.json()['detail']


def test_signed_in_with_the_permission_from_a_role_is_allowed(client, make_user):
    user = make_user(email='viewer@example.com')
    grant(user, 'ships.view')

    assert client.get(SHIPS_URL, **bearer(user)).status_code == 200


def test_superuser_has_every_permission(client, make_user):
    user = make_user(email='root@example.com', is_superuser=True)

    assert client.get(SHIPS_URL, **bearer(user)).status_code == 200


def test_authenticated_endpoint_needs_no_permissions(client, make_user):
    user = make_user(email='anyone@example.com')

    assert client.get(PROFILE_URL, **bearer(user)).status_code == 200
    assert client.get(PROFILE_URL).status_code == 401
