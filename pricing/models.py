from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.enums import CustomCostMode, CustomCostAppliesTo
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg

class SeasonShipCost(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    deck = models.TextField(null=True)
    base_per_pax = models.DecimalField(max_digits=12, decimal_places=4, null=False)
    currency = models.CharField(max_length=3, null=False)
    single_multiplier = models.DecimalField(max_digits=6, decimal_places=4, db_default=1.50, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    season = models.ForeignKey('seasons_sailings.Season', on_delete=models.CASCADE, null=False, db_index=False)
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.CASCADE, null=False, db_index=False)
    category = models.ForeignKey('catalogs.CabinCategory', on_delete=models.SET_NULL, null=True, db_index=False)
    # created_by = models.ForeignKey('myadmin.User')

    class Meta:
        db_table = 'season_ship_costs'
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='season_ship_costs_currency_check'
            ),
            models.CheckConstraint(
                check=models.Q(single_multiplier__gte=models.Value(1.0)),
                name='season_ship_costs_single_multiplier_check'
            )
        ]
        indexes = [
            models.Index(fields=['season', 'ship', 'category'], name='idx_ssc_lookup'),
        ]

class CabinCostOverride(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    base_per_pax = models.DecimalField(max_digits=12, decimal_places=4, null=False)
    currency = models.CharField(max_length=3, null=False)
    single_multiplier = models.DecimalField(max_digits=6, decimal_places=4, db_default=1.50, null=False)
    notes = models.TextField(null=True)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False, db_index=False)
    # updated_by = models.ForeignKey('myadmin.User')

    class Meta:
        db_table = 'cabin_cost_overrides'
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='cabin_cost_overrides_currency_check'
            ),
            models.CheckConstraint(
                check=models.Q(single_multiplier__gte=models.Value(1.0)),
                name='cabin_cost_overrides_single_multiplier_check'
            ),
            models.UniqueConstraint(
                fields=['sailing', 'cabin'],
                name='cabin_cost_overrides_sailing_id_cabin_id_key'
            )
        ]
        triggers = [
            set_updated_at_trg('trg_cabin_cost_ovr_updated'),
        ]

class CustomCost(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    key = models.TextField(null=False)
    label = models.TextField(null=False)
    mode = PostgresEnumField('custom_cost_mode', choices=CustomCostMode.choices, null=False)
    applies_to = PostgresEnumField('custom_cost_applies_to', choices=CustomCostAppliesTo.choices, null=False)
    is_active = models.BooleanField(db_default=True, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    ships = models.ManyToManyField('ships_cabins.Ship', related_name='ship_custom_costs', through='ShipCustomCost')

    class Meta:
        db_table = 'custom_costs'
        constraints = [
            models.UniqueConstraint(
                fields=['key'],
                name='custom_costs_key_key'
            )
        ]

class ShipCustomCost(models.Model):
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.CASCADE, null=False, db_index=False)
    custom_cost = models.ForeignKey(CustomCost, on_delete=models.CASCADE, null=False, db_index=False)
    pk = models.CompositePrimaryKey('ship_id', 'custom_cost_id')

    class Meta:
        db_table = 'ship_custom_costs'

class CabinCostCustom(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    value = models.DecimalField(max_digits=12, decimal_places=4)
    percent = models.DecimalField(max_digits=6, decimal_places=4)
    currency = models.CharField(max_length=3)

    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False, db_index=False)
    custom_cost = models.ForeignKey(CustomCost, on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'cabin_cost_customs'
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='cabin_cost_customs_currency_check'
            ),
            models.CheckConstraint(
                check=(models.Q(value__isnull=False) & models.Q(percent__isnull=True)) |
                      (models.Q(value__isnull=True) & models.Q(percent__isnull=False)),
                name='ck_custom_value'
            ),
            models.UniqueConstraint(
                fields=['sailing', 'cabin', 'custom_cost'],
                name='cabin_cost_customs_sailing_id_cabin_id_custom_cost_id_key'
            )
        ]