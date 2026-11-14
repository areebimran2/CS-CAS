"""
Tests for API access control (common/access.py): every endpoint declares who may use it, and the rules are enforced.
"""
import pytest
from django.core.exceptions import ImproperlyConfigured

from common.access import requires
from common.permissions import PERMISSIONS
from common.testing import ApiClient
from cs_cas.api import api
from myadmin.models import Permission

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

@pytest.mark.django_db
def test_no_token_is_401():
    response = ApiClient().get(SHIPS_URL)

    assert response.status_code == 401
    assert response.json()['type'] == 'NOT_AUTHENTICATED'


@pytest.mark.django_db
def test_invalid_token_is_401():
    response = ApiClient(headers={'Authorization': 'Bearer not-a-real-token'}).get(SHIPS_URL)

    assert response.status_code == 401
    assert response.json()['type'] == 'NOT_AUTHENTICATED'


def test_suspended_user_is_401(make_user):
    user = make_user(status='suspended', permissions=['ships.view'])

    assert ApiClient(user).get(SHIPS_URL).status_code == 401


def test_signed_in_without_the_permission_is_403(make_user):
    response = ApiClient(make_user()).get(SHIPS_URL)

    assert response.status_code == 403
    assert response.json()['type'] == 'PERMISSION_DENIED'
    assert 'ships.view' in response.json()['detail']


def test_signed_in_with_the_permission_from_a_role_is_allowed(make_user):
    user = make_user(permissions=['ships.view'])

    assert ApiClient(user).get(SHIPS_URL).status_code == 200


def test_superuser_has_every_permission(superuser_client):
    assert superuser_client.get(SHIPS_URL).status_code == 200


def test_authenticated_endpoint_needs_no_permissions(make_user):
    assert ApiClient(make_user()).get(PROFILE_URL).status_code == 200
    assert ApiClient().get(PROFILE_URL).status_code == 401
