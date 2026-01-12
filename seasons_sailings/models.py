from django.db import models
from django.contrib.postgres.functions import RandomUUID
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators

from common.functions import TxNow
from common.triggers import set_updated_at_trg

class Season(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    default_margin_b2b = models.DecimalField(max_digits=6, decimal_places=4, null=False)
    default_margin_b2c = models.DecimalField(max_digits=6, decimal_places=4, null=False)
    is_archived = models.BooleanField(db_default=False, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    ships = models.ManyToManyField('ships_cabins.Ship', related_name='season_ships', through='SeasonShip')

    class Meta:
        db_table = 'seasons'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='seasons_name_key'
            ),
            models.CheckConstraint(
                condition=models.Q(start_date__lte=models.F('end_date')),
                name='season_nonempty'
            ),
            ExclusionConstraint(
                index_type='GIST',
                expressions=[
                    (models.Func(models.F('start_date'), models.F('end_date') + 1,  models.Value('[)'),
                                 function='daterange', output_field=DateRangeField()), RangeOperators.OVERLAPS),
                ],
                name='seasons_no_overlap'
            )
        ]
        triggers = [
            set_updated_at_trg('trg_seasons_updated'),
        ]

class SeasonShip(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=False, db_index=False)
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.RESTRICT, null=False, db_index=False)
    pk = models.CompositePrimaryKey('season_id', 'ship_id')

    class Meta:
        db_table = 'season_ships'

class Sailing(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    departure_date = models.DateField(null=False)
    nights = models.IntegerField(null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    season = models.ForeignKey(Season, on_delete=models.RESTRICT, null=False, db_index=False)
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.RESTRICT, null=False, db_index=False)
    route = models.ForeignKey('routes.Route', on_delete=models.SET_NULL, null=True, db_index=False)

    class Meta:
        db_table = 'sailings'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(nights__gt=0),
                name='sailings_nights_check'
            ),
            ExclusionConstraint(
                index_type='GIST',
                expressions=[
                    (models.F('ship'), RangeOperators.EQUAL),
                    (models.Func(models.F('departure_date'), models.F('departure_date') + models.F('nights'), models.Value('[)'),
                                 function='daterange', output_field=DateRangeField()), RangeOperators.OVERLAPS),
                ],
                name='sailings_no_overlap_per_ship'
            )
        ]
        indexes = [
            models.Index(fields=['ship'], name='idx_sailings_ship'),
            models.Index(fields=['season'], name='idx_sailings_season'),
        ]
        triggers = [
            set_updated_at_trg('trg_sailings_updated'),
        ]

