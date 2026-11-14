"""
Shared pytest fixtures. pytest loads this file automatically, and its fixtures are available to every test.
"""
import itertools

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from common.testing import PASSWORD, ApiClient
from myadmin.models import Permission, Role

_numbers = itertools.count()


@pytest.fixture(autouse=True)
def isolated_cache(settings):
    """
    Give every test an empty in-memory cache instead of Redis, so tests never touch the development Redis and never
    see each other's data. `autouse` applies this to every test without having to request it.
    """
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    yield
    cache.clear()


@pytest.fixture
def make_user(db):
    """
    Create a user whose password is common.testing.PASSWORD. Pass `permissions` to grant them through a new role;
    any other keyword sets a user field:

        user = make_user(permissions=['ships.view'])
        suspended = make_user(email='old@example.com', status='suspended')
    """
    def make(*, permissions=(), **fields):
        n = next(_numbers)
        fields.setdefault('email', f'user{n}@example.com')
        fields.setdefault('phone', f'+447911{100000 + n % 900000}')  # valid UK mobile format
        fields.setdefault('first_name', 'Test')
        fields.setdefault('last_name', f'User {n}')
        user = get_user_model().objects.create_user(password=PASSWORD, **fields)
        if permissions:
            role = Role.objects.create(name=f'Test role {n}')
            role.permissions.set(Permission.objects.filter(key__in=permissions))
            role.users.add(user)
        return user
    return make


@pytest.fixture
def superuser(make_user):
    return make_user(is_superuser=True)


@pytest.fixture
def superuser_client(superuser):
    """An ApiClient signed in as a superuser, who has every permission."""
    return ApiClient(superuser)
