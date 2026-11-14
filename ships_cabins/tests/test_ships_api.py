"""
Tests for the ship endpoints (spec module D1), including the photo gallery. Object storage is replaced with fakes.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import MULTIPART_CONTENT

from catalogs.models import Amenity
from ships_cabins.models import Ship, ShipPhoto
from ships_cabins.services import ships as ship_service

SHIPS_URL = '/api/ships/'


@pytest.fixture
def ship(db):
    return Ship.objects.create(name='Ship A')


def test_create_ship_with_currencies_and_amenities(superuser_client, db):
    pool = Amenity.objects.create(name='Pool')

    response = superuser_client.post(SHIPS_URL, {'name': 'Ship A', 'currencies': ['EUR', 'GBP'],
                                                 'amenities': [str(pool.id)], 'new_amenities': ['Sauna']})

    assert response.status_code == 200
    assert sorted(response.json()['currencies']) == ['EUR', 'GBP']
    assert sorted(a['name'] for a in response.json()['amenities']) == ['Pool', 'Sauna']
    assert Amenity.objects.filter(name='Sauna').exists()  # new amenities join the master list


def test_replace_ship_replaces_currencies(superuser_client, ship):
    superuser_client.put(f'{SHIPS_URL}{ship.id}', {'name': 'Ship A', 'currencies': ['EUR']})

    response = superuser_client.put(f'{SHIPS_URL}{ship.id}', {'name': 'Ship A2', 'currencies': ['USD']})

    assert response.status_code == 200
    assert response.json()['name'] == 'Ship A2'
    assert response.json()['currencies'] == ['USD']


def test_upload_photos_stores_each_file(superuser_client, ship, monkeypatch):
    monkeypatch.setattr(ship_service, 'upload_file', lambda file, folder: f'https://storage.test/{folder}/{file.name}')
    files = [SimpleUploadedFile(name, b'image', content_type='image/png') for name in ('a.png', 'b.png')]

    response = superuser_client.post(f'{SHIPS_URL}{ship.id}/photos', {'files': files}, content_type=MULTIPART_CONTENT)

    assert response.status_code == 200
    assert [p['url'] for p in response.json()['photos']] == [
        f'https://storage.test/ships/{ship.id}/a.png', f'https://storage.test/ships/{ship.id}/b.png']


def test_reorder_photos_returns_them_in_the_new_order(superuser_client, ship):
    first, second = (ShipPhoto.objects.create(ship=ship, url=u, sort_order=i) for i, u in enumerate(['/1', '/2']))

    response = superuser_client.post(f'{SHIPS_URL}{ship.id}/photos/reorder',
                                     {'order': [{'id': str(first.id), 'sort_order': 5}]})

    assert response.status_code == 200
    assert [p['url'] for p in response.json()['photos']] == ['/2', '/1']


def test_delete_photo_removes_the_file_after_the_transaction_commits(superuser_client, ship, monkeypatch,
                                                                     django_capture_on_commit_callbacks):
    deleted = []
    monkeypatch.setattr(ship_service, 'delete_file', deleted.append)
    photo = ShipPhoto.objects.create(ship=ship, url='https://storage.test/x.png')

    with django_capture_on_commit_callbacks(execute=True):
        response = superuser_client.delete(f'{SHIPS_URL}{ship.id}/photos/{photo.id}')

    assert response.status_code == 204
    assert not ShipPhoto.objects.filter(id=photo.id).exists()
    assert deleted == ['https://storage.test/x.png']
