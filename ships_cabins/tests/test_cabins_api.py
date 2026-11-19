"""
Tests for the cabin endpoints (spec module D3).
"""
import pytest

from catalogs.models import CabinCategory
from ships_cabins.models import Cabin, CabinMap, CabinMapZone, Ship
from ships_cabins.services.cabins import cabins_matching


@pytest.fixture
def ship(db):
    return Ship.objects.create(name='Bellissima')


@pytest.fixture
def suite(db):
    return CabinCategory.objects.get(name='Suite')  # seeded by catalogs/migrations/0002_seed_data.py


def cabins_url(ship, *path):
    return '/'.join([f'/api/ships/{ship.id}/cabins', *map(str, path)])


def cabin(number, category, **fields):
    return {'number': number, 'category_id': str(category.id), **fields}


def add_cabin(ship, number, category, **fields):
    return Cabin.objects.create(ship=ship, number=number, name=f'Cabin {number}', category=category, **fields)


# -- Create

def test_create_cabin_defaults_its_name(superuser_client, ship, suite):
    response = superuser_client.post(cabins_url(ship), cabin(' 402 ', suite, deck='Main'))

    assert response.status_code == 200
    body = response.json()
    assert (body['number'], body['name'], body['deck']) == ('402', 'Cabin 402', 'Main')
    assert body['category'] == {'id': str(suite.id), 'name': 'Suite'}


def test_cabin_numbers_are_unique_per_ship_ignoring_case(superuser_client, ship, suite):
    add_cabin(ship, '12A', suite)
    other_ship = Ship.objects.create(name='Aretis')

    assert superuser_client.post(cabins_url(ship), cabin('12a', suite)).status_code == 409
    assert superuser_client.post(cabins_url(other_ship), cabin('12A', suite)).status_code == 200


def test_inactive_category_is_rejected(superuser_client, ship):
    retired = CabinCategory.objects.create(name='Retired', is_active=False)

    response = superuser_client.post(cabins_url(ship), cabin('1', retired))

    assert response.status_code == 422
    assert response.json()['errors'][0]['field'] == 'category_id'


def test_archived_ship_takes_no_new_cabins(superuser_client, ship, suite):
    Ship.objects.filter(id=ship.id).update(is_archived=True)

    response = superuser_client.post(cabins_url(ship), cabin('1', suite))

    assert response.status_code == 409
    assert response.json()['type'] == 'SHIP_ARCHIVED'


def test_bulk_create(superuser_client, ship, suite):
    response = superuser_client.post(cabins_url(ship, 'bulk'), {'cabins': [cabin('1', suite), cabin('2', suite)]})

    assert response.status_code == 200
    assert sorted(c['number'] for c in response.json()) == ['1', '2']


def test_bulk_create_is_all_or_nothing_and_reports_every_row(superuser_client, ship, suite):
    add_cabin(ship, '5', suite)
    retired = CabinCategory.objects.create(name='Retired', is_active=False)
    rows = [cabin('1', suite), cabin('5', suite), cabin('7', suite), cabin('7', retired)]

    response = superuser_client.post(cabins_url(ship, 'bulk'), {'cabins': rows})

    assert response.status_code == 422
    assert [error['field'] for error in response.json()['errors']] == [
        'cabins[1].number', 'cabins[3].number', 'cabins[3].category_id']
    assert ship.cabin_set.count() == 1  # nothing was saved, not even the valid row


# -- Read

def test_list_is_in_natural_number_order(superuser_client, ship, suite):
    for number in ['19', '3', '12A', '10', '12']:
        add_cabin(ship, number, suite)

    response = superuser_client.get(cabins_url(ship))

    assert [c['number'] for c in response.json()['items']] == ['3', '10', '12', '12A', '19']


def test_list_filters(superuser_client, ship, suite):
    balcony = CabinCategory.objects.get(name='Balcony')
    add_cabin(ship, '1', suite, deck='Main')
    add_cabin(ship, '2', balcony, deck='Main')
    add_cabin(ship, '3', balcony, deck='Lower')
    add_cabin(ship, '4', balcony, deck='Lower', is_archived=True)

    def numbers(query):
        return [c['number'] for c in superuser_client.get(cabins_url(ship) + query).json()['items']]

    assert numbers('?deck=Main') == ['1', '2']
    assert numbers(f'?category_id={balcony.id}') == ['2', '3']
    assert numbers(f'?category_id={balcony.id}&category_id={suite.id}&deck=Main') == ['1', '2']
    assert numbers('?archived=all&deck=Lower') == ['3', '4']


def test_decks_lists_current_cabins_per_deck(superuser_client, ship, suite):
    add_cabin(ship, '1', suite, deck='Main')
    add_cabin(ship, '2', suite, deck='Main')
    add_cabin(ship, '3', suite, deck='Lower')
    add_cabin(ship, '4', suite, deck='Lower', is_archived=True)
    add_cabin(ship, '5', suite)  # no deck

    response = superuser_client.get(cabins_url(ship, 'decks'))

    assert response.json() == [{'deck': 'Lower', 'cabin_count': 1}, {'deck': 'Main', 'cabin_count': 2}]


def test_cabin_of_another_ship_is_404(superuser_client, ship, suite):
    other = add_cabin(Ship.objects.create(name='Aretis'), '1', suite)

    assert superuser_client.get(cabins_url(ship, other.id)).status_code == 404


# -- Update, archive and delete

def test_update_changes_only_the_fields_sent(superuser_client, ship, suite):
    existing = add_cabin(ship, '1', suite, deck='Main', notes='Near the lift')

    response = superuser_client.put(cabins_url(ship, existing.id), {'deck': 'Lower', 'name': ''})

    assert response.status_code == 200
    body = response.json()
    assert (body['deck'], body['notes'], body['name']) == ('Lower', 'Near the lift', 'Cabin 1')


def test_archive_and_unarchive(superuser_client, ship, suite):
    existing = add_cabin(ship, '1', suite)

    assert superuser_client.post(cabins_url(ship, f'{existing.id}/archive')).json()['is_archived'] is True
    assert superuser_client.post(cabins_url(ship, f'{existing.id}/unarchive')).json()['is_archived'] is False


def test_delete_unused_cabin(superuser_client, ship, suite):
    existing = add_cabin(ship, '1', suite)

    assert superuser_client.delete(cabins_url(ship, existing.id)).status_code == 204
    assert not Cabin.objects.exists()


def test_delete_cabin_on_a_map_is_refused(superuser_client, ship, suite):
    existing = add_cabin(ship, '1', suite)
    cabin_map = CabinMap.objects.create(ship=ship, version=1)
    CabinMapZone.objects.create(map=cabin_map, cabin=existing, polygon={})

    response = superuser_client.delete(cabins_url(ship, existing.id))

    assert response.status_code == 409
    assert 'cabin map zones' in response.json()['detail']


# -- Bulk pricing target

def test_cabins_matching_selects_current_cabins_by_category_and_deck(ship, suite):
    balcony = CabinCategory.objects.get(name='Balcony')
    add_cabin(ship, '1', suite, deck='Main')
    add_cabin(ship, '2', balcony, deck='Main')
    add_cabin(ship, '3', suite, deck='Main', is_archived=True)

    matching = cabins_matching(ship, category_ids=[suite.id], decks=['Main'])

    assert [c.number for c in matching] == ['1']
