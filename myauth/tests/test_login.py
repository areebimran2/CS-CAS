"""
Tests for POST /api/auth/login, the first step of signing in (spec module A1).
"""
import pytest
from django.contrib.auth import get_user_model

LOGIN_URL = '/api/auth/login'
PASSWORD = 'correct-horse-battery-staple'


@pytest.fixture
def user(db):
    """A user with no 2FA device set up yet. The `db` fixture gives the test access to the test database."""
    return get_user_model().objects.create_user(
        email='sales@example.com',
        password=PASSWORD,
        first_name='Sam',
        last_name='Sales',
        phone='+447700900123',
    )


def test_login_with_correct_password_starts_verification(client, user):
    response = client.post(LOGIN_URL, {'email': user.email, 'password': PASSWORD}, content_type='application/json')

    assert response.status_code == 200
    body = response.json()
    assert body['id'].startswith('verif.')
    assert body['method'] is None


def test_login_with_wrong_password_is_rejected(client, user):
    response = client.post(LOGIN_URL, {'email': user.email, 'password': 'wrong'}, content_type='application/json')

    assert response.status_code == 401
    assert response.json()['title'] == 'Invalid credentials'


def test_login_email_is_case_insensitive(client, user):
    response = client.post(LOGIN_URL, {'email': 'SALES@example.com', 'password': PASSWORD},
                           content_type='application/json')

    assert response.status_code == 200
