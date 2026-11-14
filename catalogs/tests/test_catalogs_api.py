"""
Tests for the catalogue endpoints (spec module C): amenities, cabin categories, custom costs, FX, reserve settings and
cancellation policies.
"""
import pytest
from django.db import IntegrityError

from catalogs.models import CancellationPolicy, ExchangeRatesManual

POLICIES_URL = '/api/policies/cancellation-policies/'


@pytest.mark.parametrize('url, payload, change', [
    ('/api/catalog/amenities/', {'name': 'Spa', 'is_active': True}, {'name': 'Thermal spa'}),
    ('/api/catalog/cabin-categories/', {'name': 'Studio', 'is_active': True}, {'sort_order': 5}),
    ('/api/catalog/custom-costs/',
     {'key': 'port_fees', 'label': 'Port fees', 'mode': 'fixed', 'applies_to': 'per_cabin', 'is_active': True},
     {'label': 'Port charges'}),
])
def test_create_then_partially_update(superuser_client, url, payload, change):
    created = superuser_client.post(url, payload)
    assert created.status_code == 200

    updated = superuser_client.put(f"{url}{created.json()['id']}", change)

    assert updated.status_code == 200
    assert updated.json() == {**created.json(), **change}


def test_manual_rates_upsert_updates_existing_pairs(superuser_client):
    superuser_client.put('/api/fx/manual-rates', {'rates': [{'base': 'EUR', 'quote': 'GBP', 'rate': '0.85'}]})
    superuser_client.put('/api/fx/manual-rates', {'rates': [{'base': 'EUR', 'quote': 'GBP', 'rate': '0.86'}]})

    assert list(ExchangeRatesManual.objects.values_list('base', 'quote')) == [('EUR', 'GBP')]
    assert str(ExchangeRatesManual.objects.get().rate) == '0.86000000'


def test_reserve_settings_update_changes_only_the_fields_sent(superuser_client):
    response = superuser_client.put('/api/policies/reserve-settings/',
                                    {'max_hold_minutes': 720, 'reminder_schedule_minutes': [60]})

    assert response.status_code == 200
    body = response.json()
    assert (body['max_hold_minutes'], body['reminder_schedule_minutes']) == (720, [60])
    assert body['extension_minutes'] == 1440  # seeded default, untouched


def tier(min_days, max_days, value):
    return {'min_days': min_days, 'max_days': max_days, 'charge_type': 'percent_total', 'value': value}


def test_cancellation_policy_replace_swaps_all_tiers(superuser_client):
    created = superuser_client.post(POLICIES_URL, {'name': 'Standard',
                                                   'tiers': [tier(0, 30, '1'), tier(31, 365, '0.5')]})

    replaced = superuser_client.put(f"{POLICIES_URL}{created.json()['id']}",
                                    {'name': 'Strict', 'tiers': [tier(0, 365, '1')]})

    assert replaced.status_code == 200
    assert replaced.json()['name'] == 'Strict'
    assert [(t['min_days'], t['max_days']) for t in replaced.json()['tiers']] == [(0, 365)]


def test_cancellation_policy_replace_is_all_or_nothing(superuser_client):
    """A tier with min_days > max_days breaks a database constraint, so the old tiers must survive."""
    created = superuser_client.post(POLICIES_URL, {'name': 'Standard', 'tiers': [tier(0, 30, '1')]})
    policy = CancellationPolicy.objects.get(id=created.json()['id'])

    with pytest.raises(IntegrityError):
        superuser_client.put(f'{POLICIES_URL}{policy.id}', {'name': 'Broken', 'tiers': [tier(40, 10, '1')]})

    policy.refresh_from_db()
    assert policy.name == 'Standard'
    assert list(policy.cancellationpolicytier_set.values_list('min_days', 'max_days')) == [(0, 30)]
