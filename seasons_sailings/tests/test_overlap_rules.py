"""
The database itself must reject overlapping seasons and overlapping sailings for one ship (spec sections F1 and F2).
These rules are exclusion constraints, so the tests save models directly rather than going through the API.
"""
from datetime import date

import pytest
from django.db import IntegrityError

from seasons_sailings.models import Season, Sailing
from ships_cabins.models import Ship

pytestmark = pytest.mark.django_db  # every test in this file uses the test database


def make_season(name, start, end):
    return Season.objects.create(name=name, start_date=start, end_date=end,
                                 default_margin_b2b='0.15', default_margin_b2c='0.25')


def test_seasons_that_share_a_day_are_rejected():
    make_season('2025/26', date(2025, 9, 1), date(2026, 8, 31))

    # The end date is inclusive, so starting on 31 August 2026 overlaps by one day.
    with pytest.raises(IntegrityError):
        make_season('2026/27', date(2026, 8, 31), date(2027, 8, 31))


def test_back_to_back_seasons_are_allowed():
    make_season('2025/26', date(2025, 9, 1), date(2026, 8, 31))
    make_season('2026/27', date(2026, 9, 1), date(2027, 8, 31))

    assert Season.objects.count() == 2


def test_overlapping_sailings_on_one_ship_are_rejected():
    season = make_season('2025/26', date(2025, 9, 1), date(2026, 8, 31))
    ship = Ship.objects.create(name='Ship A')
    Sailing.objects.create(season=season, ship=ship, departure_date=date(2025, 10, 1), nights=7)

    # The first sailing runs 1-8 October; departing on 5 October clashes with it.
    with pytest.raises(IntegrityError):
        Sailing.objects.create(season=season, ship=ship, departure_date=date(2025, 10, 5), nights=5)


def test_sailing_can_depart_on_the_day_the_previous_one_returns():
    season = make_season('2025/26', date(2025, 9, 1), date(2026, 8, 31))
    ship = Ship.objects.create(name='Ship A')
    Sailing.objects.create(season=season, ship=ship, departure_date=date(2025, 10, 1), nights=7)
    Sailing.objects.create(season=season, ship=ship, departure_date=date(2025, 10, 8), nights=5)

    assert Sailing.objects.count() == 2
