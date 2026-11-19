"""
Tests for the route endpoints (spec module E1).
"""
import pytest

ROUTES_URL = '/api/routes'


def leg(seq, place_id):
    return {'seq': seq, 'place_id': place_id, 'lat': 43.5, 'lng': 16.4, 'tz': 'Europe/Zagreb'}


def place_ids(route):
    return [leg['place_id'] for leg in route['legs']]


@pytest.fixture
def route(superuser_client):
    response = superuser_client.post(ROUTES_URL, {'name': 'Dalmatia', 'legs': [leg(1, 'split'), leg(2, 'hvar')]})
    assert response.status_code == 200
    return response.json()


def test_create_route_with_legs(route):
    assert place_ids(route) == ['split', 'hvar']


def test_update_without_legs_keeps_them(superuser_client, route):
    response = superuser_client.put(f"{ROUTES_URL}/{route['id']}", {'name': 'Dalmatian islands'})

    assert response.status_code == 200
    assert response.json()['name'] == 'Dalmatian islands'
    assert place_ids(response.json()) == ['split', 'hvar']


def test_update_with_legs_replaces_them(superuser_client, route):
    response = superuser_client.put(f"{ROUTES_URL}/{route['id']}", {'legs': [leg(1, 'dubrovnik')]})

    assert place_ids(response.json()) == ['dubrovnik']
