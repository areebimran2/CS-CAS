"""
Helpers for tests. The matching pytest fixtures (make_user, superuser, superuser_client) are in conftest.py.
"""
from django.test import Client
from ninja_jwt.tokens import AccessToken

PASSWORD = 'correct-horse-battery-staple'  # the password of every user made by the make_user fixture


class ApiClient(Client):
    """
    Django's test client, signed in as `user` when one is given, and sending JSON bodies by default:

        ApiClient(user).post('/api/routes/', {'name': 'Adriatic', 'legs': [...]})
    """

    def __init__(self, user=None, **kwargs):
        headers = kwargs.pop('headers', {})
        if user is not None:
            headers['Authorization'] = f'Bearer {AccessToken.for_user(user)}'
        super().__init__(headers=headers, **kwargs)

    def post(self, path, data=None, content_type='application/json', **extra):
        return super().post(path, data, content_type=content_type, **extra)

    def put(self, path, data=None, content_type='application/json', **extra):
        return super().put(path, data, content_type=content_type, **extra)

    def patch(self, path, data=None, content_type='application/json', **extra):
        return super().patch(path, data, content_type=content_type, **extra)
