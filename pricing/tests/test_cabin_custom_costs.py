"""
A per-cabin custom cost stores either a fixed value or a percentage, never both (spec section G2).
Regression test: these columns used to be NOT NULL, so no row could ever be saved.
"""
from datetime import date

import pytest
from django.db import IntegrityError

from catalogs.models import CabinCategory, CustomCost
from pricing.models import CabinCostCustom
from seasons_sailings.models import Season, Sailing
from ships_cabins.models import Ship, Cabin

pytestmark = pytest.mark.django_db


@pytest.fixture
def cabin_and_sailing():
    ship = Ship.objects.create(name='Ship A')
    # 'Premium' comes from the seed data migration, so this also checks the seed data was applied.
    cabin = Cabin.objects.create(ship=ship, name='Cabin 402', number='402',
                                 category=CabinCategory.objects.get(name='Premium'))
    season = Season.objects.create(name='2025/26', start_date=date(2025, 9, 1), end_date=date(2026, 8, 31),
                                   default_margin_b2b='0.15', default_margin_b2c='0.25')
    sailing = Sailing.objects.create(season=season, ship=ship, departure_date=date(2025, 10, 1), nights=7)
    return cabin, sailing


@pytest.fixture
def port_fees():
    return CustomCost.objects.create(key='port_fees', label='Port fees', mode='fixed', applies_to='per_cabin')


def test_fixed_value_custom_cost_can_be_saved(cabin_and_sailing, port_fees):
    cabin, sailing = cabin_and_sailing

    CabinCostCustom.objects.create(cabin=cabin, sailing=sailing, custom_cost=port_fees, value='50', currency='EUR')

    assert CabinCostCustom.objects.count() == 1


def test_value_and_percent_together_are_rejected(cabin_and_sailing, port_fees):
    cabin, sailing = cabin_and_sailing

    with pytest.raises(IntegrityError):
        CabinCostCustom.objects.create(cabin=cabin, sailing=sailing, custom_cost=port_fees,
                                       value='50', percent='0.1', currency='EUR')
