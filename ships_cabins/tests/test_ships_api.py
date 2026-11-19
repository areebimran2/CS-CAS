"""
Tests for the ship endpoints (spec module D1), including the photo gallery. Object storage is replaced with fakes.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.client import MULTIPART_CONTENT
from django.test.utils import CaptureQueriesContext

from catalogs.models import Amenity, CabinCategory
from ships_cabins.models import Cabin, Ship, ShipPhoto
from ships_cabins.services import ships as ship_service

SHIPS_URL = '/api/ships/'


@pytest.fixture
def ship(db):
    return Ship.objects.create(name='Bellissima')


def ship_payload(**overrides):
    return {'name': 'Bellissima', 'currencies': ['EUR'], **overrides}


# -- Create and replace

def test_create_ship_with_currencies_and_amenities(superuser_client, db):
    pool = Amenity.objects.create(name='Pool')

    response = superuser_client.post(SHIPS_URL, ship_payload(
        currencies=['EUR', 'GBP', 'EUR'], amenity_ids=[str(pool.id)], new_amenities=['Sauna'],
        address={'line1': 'Obala 1', 'city': 'Split', 'country': 'HR'}))

    assert response.status_code == 200
    body = response.json()
    assert sorted(body['currencies']) == ['EUR', 'GBP']  # the duplicate is dropped
    assert sorted(a['name'] for a in body['amenities']) == ['Pool', 'Sauna']
    assert body['address']['country'] == 'HR'
    assert Amenity.objects.filter(name='Sauna').exists()  # new amenities join the master list


def test_ship_names_are_unique_ignoring_case(superuser_client, ship):
    response = superuser_client.post(SHIPS_URL, ship_payload(name='BELLISSIMA'))

    assert response.status_code == 409
    assert response.json()['type'] == 'DUPLICATE'
    assert response.json()['errors'] == [{'field': 'name', 'message': 'Already in use'}]


@pytest.mark.parametrize('payload', [
    ship_payload(currencies=[]),
    ship_payload(name='   '),
    ship_payload(address={'line1': 'Obala 1', 'city': 'Split', 'country': 'XX'}),
])
def test_invalid_ship_is_rejected(superuser_client, db, payload):
    assert superuser_client.post(SHIPS_URL, payload).status_code == 422


def test_inactive_amenity_is_rejected(superuser_client, db):
    retired = Amenity.objects.create(name='Casino', is_active=False)

    response = superuser_client.post(SHIPS_URL, ship_payload(amenity_ids=[str(retired.id)]))

    assert response.status_code == 422
    assert response.json()['errors'][0]['field'] == 'amenity_ids'
    assert not Ship.objects.exists()


def test_new_amenity_reuses_an_existing_one_regardless_of_case(superuser_client, db):
    pool = Amenity.objects.create(name='Pool')

    response = superuser_client.post(SHIPS_URL, ship_payload(new_amenities=['pool']))

    assert [a['id'] for a in response.json()['amenities']] == [str(pool.id)]
    assert Amenity.objects.count() == 1


def test_replace_clears_fields_that_are_left_out(superuser_client, db):
    created = superuser_client.post(SHIPS_URL, ship_payload(operator='Katarina Line', currencies=['EUR', 'GBP'])).json()

    response = superuser_client.put(f"{SHIPS_URL}{created['id']}", ship_payload(currencies=['USD']))

    assert response.status_code == 200
    assert response.json()['operator'] is None
    assert response.json()['currencies'] == ['USD']


def test_replace_keeps_an_amenity_deactivated_since_it_was_added(superuser_client, ship):
    spa = Amenity.objects.create(name='Spa')
    ship.amenities.add(spa)
    Amenity.objects.filter(id=spa.id).update(is_active=False)

    response = superuser_client.put(f'{SHIPS_URL}{ship.id}', ship_payload(amenity_ids=[str(spa.id)]))

    assert response.status_code == 200
    assert [a['name'] for a in response.json()['amenities']] == ['Spa']


# -- List and detail

def test_list_hides_archived_ships_unless_asked(superuser_client, db):
    Ship.objects.create(name='Aretis')
    Ship.objects.create(name='Memories', is_archived=True)

    def names(query=''):
        return [s['name'] for s in superuser_client.get(f'{SHIPS_URL}{query}').json()['items']]

    assert names() == ['Aretis']
    assert names('?archived=true') == ['Memories']
    assert names('?archived=all') == ['Aretis', 'Memories']
    assert names('?archived=all&search=mem') == ['Memories']


def test_list_runs_the_same_number_of_queries_for_any_number_of_ships(superuser_client, db):
    def queries_for_list():
        with CaptureQueriesContext(connection) as context:
            superuser_client.get(SHIPS_URL)
        return len(context.captured_queries)

    category = CabinCategory.objects.get(name='Suite')
    Ship.objects.create(name='Ship 1')
    one_ship = queries_for_list()
    for n in range(2, 5):
        ship = Ship.objects.create(name=f'Ship {n}')
        Cabin.objects.create(ship=ship, number='1', name='Cabin 1', category=category)

    assert queries_for_list() == one_ship


def test_detail_counts_current_cabins(superuser_client, ship):
    category = CabinCategory.objects.get(name='Suite')
    Cabin.objects.create(ship=ship, number='1', name='Cabin 1', category=category)
    Cabin.objects.create(ship=ship, number='2', name='Cabin 2', category=category, is_archived=True)

    assert superuser_client.get(f'{SHIPS_URL}{ship.id}').json()['cabin_count'] == 1


def test_invalid_ship_id_is_422(superuser_client, db):
    assert superuser_client.get(f'{SHIPS_URL}not-a-uuid').status_code == 422


# -- Archive and delete

def test_archive_and_unarchive(superuser_client, ship):
    assert superuser_client.post(f'{SHIPS_URL}{ship.id}/archive').json()['is_archived'] is True
    assert superuser_client.post(f'{SHIPS_URL}{ship.id}/unarchive').json()['is_archived'] is False


def test_delete_unused_ship_removes_what_it_owns(superuser_client, ship, monkeypatch,
                                                 django_capture_on_commit_callbacks):
    deleted_files = []
    monkeypatch.setattr(ship_service, 'delete_file', deleted_files.append)
    ship.shipcurrency_set.create(currency='EUR')
    ShipPhoto.objects.create(ship=ship, url='https://storage.test/a.png')

    with django_capture_on_commit_callbacks(execute=True):
        response = superuser_client.delete(f'{SHIPS_URL}{ship.id}')

    assert response.status_code == 204
    assert not Ship.objects.exists()
    assert deleted_files == ['https://storage.test/a.png']


def test_delete_ship_with_cabins_is_refused(superuser_client, ship):
    Cabin.objects.create(ship=ship, number='1', name='Cabin 1', category=CabinCategory.objects.get(name='Suite'))

    response = superuser_client.delete(f'{SHIPS_URL}{ship.id}')

    assert response.status_code == 409
    assert response.json()['type'] == 'IN_USE'
    assert 'cabins' in response.json()['detail']
    assert Ship.objects.filter(id=ship.id).exists()


def test_deleting_needs_its_own_permission(make_user, ship):
    from common.testing import ApiClient
    editor = make_user(permissions=['ships.edit'])

    assert ApiClient(editor).delete(f'{SHIPS_URL}{ship.id}').status_code == 403


# -- Photos

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
