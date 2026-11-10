from django.db import models
from django.contrib.postgres.functions import RandomUUID

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

    created_by = models.ForeignKey('myauth.User', on_delete=models.DO_NOTHING, null=True,
                                   db_index=False, db_column='created_by')

    class Meta:
        db_table = 'season_ship_costs'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='season_ship_costs_currency_check'
            ),
            models.CheckConstraint(
                condition=models.Q(single_multiplier__gte=models.Value(1.0)),
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

    updated_by = models.ForeignKey('myauth.User', on_delete=models.DO_NOTHING, null=True,
                                   db_index=False, db_column='updated_by')
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'cabin_cost_overrides'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='cabin_cost_overrides_currency_check'
            ),
            models.CheckConstraint(
                condition=models.Q(single_multiplier__gte=models.Value(1.0)),
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

# The custom costs catalogue (CustomCost) is admin-managed and lives in catalogs.models. Pricing owns which costs
# apply to each ship (ShipCustomCost) and their values per cabin and sailing (CabinCostCustom).

class ShipCustomCost(models.Model):
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.CASCADE, null=False, db_index=False)
    custom_cost = models.ForeignKey('catalogs.CustomCost', on_delete=models.CASCADE, null=False, db_index=False)
    pk = models.CompositePrimaryKey('ship_id', 'custom_cost_id')

    class Meta:
        db_table = 'ship_custom_costs'

class CabinCostCustom(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    # Exactly one of value (mode=fixed) or percent (mode=percent, 0..1) is set; see ck_custom_value.
    value = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    percent = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    currency = models.CharField(max_length=3, null=True)

    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False, db_index=False)
    custom_cost = models.ForeignKey('catalogs.CustomCost', on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'cabin_cost_customs'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='cabin_cost_customs_currency_check'
            ),
            models.CheckConstraint(
                condition=(models.Q(value__isnull=False) & models.Q(percent__isnull=True)) |
                      (models.Q(value__isnull=True) & models.Q(percent__isnull=False)),
                name='ck_custom_value'
            ),
            models.UniqueConstraint(
                fields=['sailing', 'cabin', 'custom_cost'],
                name='cabin_cost_customs_sailing_id_cabin_id_custom_cost_id_key'
            )
        ]