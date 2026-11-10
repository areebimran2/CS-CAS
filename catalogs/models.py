"""
Admin-managed reference data and policies (spec module C. Catalogues). Other apps read these; they do not depend on
any other domain app, apart from the user model for audit columns.
"""
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.functions import RandomUUID
from django.db import models

from common.enums import CustomCostMode, CustomCostAppliesTo, CancellationChargeType
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg


# -- C1. Amenities

class Amenity(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    is_active = models.BooleanField(db_default=True, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'amenities'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='amenities_name_key'
            )
        ]
        triggers = [
            set_updated_at_trg('trg_amenities_updated'),
        ]


# -- C2. Cabin Categories

class CabinCategory(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    sort_order = models.IntegerField(db_default=100, null=False)
    is_active = models.BooleanField(db_default=True, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'cabin_categories'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='cabin_categories_name_key'
            )
        ]
        triggers = [
            set_updated_at_trg('trg_cabin_cat_updated'),
        ]


# -- C3. Custom Costs

class CustomCost(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    key = models.TextField(null=False)
    label = models.TextField(null=False)
    mode = PostgresEnumField('custom_cost_mode', choices=CustomCostMode.choices, null=False)
    applies_to = PostgresEnumField('custom_cost_applies_to', choices=CustomCostAppliesTo.choices, null=False)
    is_active = models.BooleanField(db_default=True, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'custom_costs'
        constraints = [
            models.UniqueConstraint(
                fields=['key'],
                name='custom_costs_key_key'
            )
        ]


# -- C4. Exchange rates

class ExchangeRatesManual(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    base = models.CharField(max_length=3, null=False)
    quote = models.CharField(max_length=3, null=False)
    rate = models.DecimalField(max_digits=18, decimal_places=8, null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'exchange_rates_manual'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base__regex=r'^[A-Z]{3}$'),
                name='exchange_rates_manual_base_check'
            ),
            models.CheckConstraint(
                condition=models.Q(quote__regex=r'^[A-Z]{3}$'),
                name='exchange_rates_manual_quote_check'
            ),
            models.CheckConstraint(
                condition=models.Q(rate__gt=models.Value(0)),
                name='exchange_rates_manual_rate_check'
            ),
            models.UniqueConstraint(
                fields=['base', 'quote'],
                name='exchange_rates_manual_base_quote_key'
            )
        ]

class FXRatesCache(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    provider = models.TextField(null=False)
    base = models.CharField(max_length=3, null=False)
    quote = models.CharField(max_length=3, null=False)
    rate = models.DecimalField(max_digits=18, decimal_places=8, null=False)
    fetched_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'fx_rates_cache'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base__regex=r'^[A-Z]{3}$'),
                name='fx_rates_cache_base_check'
            ),
            models.CheckConstraint(
                condition=models.Q(quote__regex=r'^[A-Z]{3}$'),
                name='fx_rates_cache_quote_check'
            ),
            models.CheckConstraint(
                condition=models.Q(rate__gt=models.Value(0)),
                name='fx_rates_cache_rate_check'
            ),
            models.UniqueConstraint(
                fields=['provider', 'base', 'quote'],
                name='fx_rates_cache_provider_base_quote_key'
            )
        ]


# -- C5. Reserve Settings

class ReserveSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    max_hold_minutes = models.IntegerField(db_default=2880, null=False) # -- e.g., 48h
    reminder_schedule_minutes = ArrayField(base_field=models.IntegerField(), db_default='{2880, 1440}', null=False) # -- 2d,1d before
    allow_extensions = models.BooleanField(db_default=True, null=False)
    max_extensions = models.IntegerField(db_default=1, null=False)
    extension_minutes = models.IntegerField(db_default=1440, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    created_by = models.ForeignKey('myauth.User', on_delete=models.DO_NOTHING, null=True,
                                   db_index=False, db_column='created_by')

    class Meta:
        db_table = 'reserve_settings'


# -- C6. Cancellation Policies

class CancellationPolicy(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    non_refundable = models.BooleanField(db_default=False, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'cancellation_policies'

class CancellationPolicyTier(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    min_days = models.IntegerField(null=False)
    max_days = models.IntegerField(null=False)
    charge_type = PostgresEnumField('cancellation_charge_type', choices=CancellationChargeType.choices, null=False)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=False)

    policy = models.ForeignKey(CancellationPolicy, on_delete=models.CASCADE, null=False, db_index=False)

    class Meta:
        db_table = 'cancellation_policy_tiers'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(min_days__lte=models.F('max_days')),
                name='ck_days_order'
            )
        ]


# -- Global settings (key/value)

class Setting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.JSONField(null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'settings'
