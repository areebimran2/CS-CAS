"""
Tests for POST /api/auth/login, the first step of signing in (spec module A1).
"""
from common.testing import PASSWORD, ApiClient

LOGIN_URL = '/api/auth/login'


def test_login_with_correct_password_starts_verification(make_user):
    user = make_user()  # no 2FA device set up yet

    response = ApiClient().post(LOGIN_URL, {'email': user.email, 'password': PASSWORD})

    assert response.status_code == 200
    body = response.json()
    assert body['id'].startswith('verif.')  # verification context id, used for the 2FA step
    assert body['method'] is None  # no 2FA device yet


def test_login_with_wrong_password_is_rejected(make_user):
    user = make_user()

    response = ApiClient().post(LOGIN_URL, {'email': user.email, 'password': 'wrong'})

    assert response.status_code == 401
    assert response.json()['title'] == 'Invalid credentials'


def test_login_email_is_case_insensitive(make_user):
    make_user(email='sales@example.com')

    response = ApiClient().post(LOGIN_URL, {'email': 'SALES@example.com', 'password': PASSWORD})

    assert response.status_code == 200
