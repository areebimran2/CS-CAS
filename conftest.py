import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def isolated_cache(settings):
    """
    Give every test an empty in-memory cache instead of Redis, so tests never touch the development Redis and never
    see each other's data. `autouse` applies this to every test without having to request it.
    """
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    yield
    cache.clear()
