"""
Tests for the admin endpoints (spec module B): users and roles.
"""
import pytest

from myadmin.models import Role
from myauth.models import User

STRONG_PASSWORD = 'a-long-and-unusual-passphrase'


@pytest.fixture
def sales_role(db):
    return Role.objects.get(name='Sales')  # seeded by myadmin/migrations/0002_seed_data.py


def new_user_payload(role, **overrides):
    return {'first_name': 'Sam', 'last_name': 'Sales', 'designation': 'Sales executive',
            'email': 'sam@example.com', 'phone': '+447911000001', 'password': STRONG_PASSWORD,
            'role_id': str(role.id), **overrides}


def test_create_user_sets_password_role_and_preferences(superuser_client, sales_role):
    response = superuser_client.post('/api/admin/users', new_user_payload(sales_role))

    assert response.status_code == 200
    assert [role['name'] for role in response.json()['roles']] == ['Sales']
    user = User.objects.get(email='sam@example.com')
    assert user.check_password(STRONG_PASSWORD)
    assert user.preferences.fx_mode == 'manual'


def test_update_user_changes_only_the_fields_sent(superuser_client, make_user):
    user = make_user()

    response = superuser_client.put(f'/api/admin/users/{user.id}', {'designation': 'Team lead'})

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.designation == 'Team lead'
    assert user.first_name == 'Test'


def test_rename_role_keeps_its_permissions(superuser_client):
    created = superuser_client.post('/api/admin/roles', {'name': 'Auditor', 'permissions': ['ships.view']})

    renamed = superuser_client.put(f"/api/admin/roles/{created.json()['id']}", {'name': 'Ship auditor'})

    assert renamed.status_code == 200
    assert renamed.json()['permissions'] == ['ships.view']


def test_role_permissions_are_replaced_on_update(superuser_client):
    created = superuser_client.post('/api/admin/roles', {'name': 'Auditor', 'permissions': ['ships.view']})
    assert created.json()['permissions'] == ['ships.view']

    updated = superuser_client.put(f"/api/admin/roles/{created.json()['id']}",
                                   {'permissions': ['routes.view', 'seasons.view']})

    assert updated.status_code == 200
    assert sorted(updated.json()['permissions']) == ['routes.view', 'seasons.view']
