from django.db import models
from django.db.models.functions import Now
from django.contrib.postgres.functions import RandomUUID
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class SeasonShipCost(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    season = models.ForeignKey('seasons_sailings.Season', on_delete=models.CASCADE, null=False)
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.CASCADE, null=False)
    category = models.ForeignKey('catalogs.CabinCategory', on_delete=models.SET_NULL, null=True)
    deck = models.TextField()
    base_per_pax = models.DecimalField(max_digits=12, decimal_places=4, null=False)
    currency = models.CharField(max_length=3, null=False)
    single_multiplier = models.DecimalField(max_digits=6, decimal_places=4, default=1.50, db_default=1.50, null=False)
    # created_by = models.ForeignKey('myadmin.User')
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='ship_cost_currency_format_check'
            ),
            models.CheckConstraint(
                check=models.Q(single_multiplier__gte=1.0),
                name='ship_cost_multiplier_validity_check'
            )
        ]

class CabinCostOverride(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False)
    base_per_pax = models.DecimalField(max_digits=12, decimal_places=4, null=False)
    currency = models.CharField(max_length=3, null=False)
    single_multiplier = models.DecimalField(max_digits=6, decimal_places=4, default=1.50, db_default=1.50, null=False)
    notes = models.TextField()
    # updated_by = models.ForeignKey('myadmin.User')
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='override_currency_format_check'
            ),
            models.CheckConstraint(
                check=models.Q(single_multiplier__gte=1.0),
                name='override_single_multiplier_validity_check'
            ),
            models.UniqueConstraint(
                fields=['sailing', 'cabin'],
                name='unique_sailing_cabin'
            )
        ]

class CustomCost(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    key = models.TextField(unique=True, null=False)
    label = models.TextField(null=False)

    class Mode(models.TextChoices):
        FIXED = "fixed", _("Fixed")
        PERCENT = "percent", _("Percent")

    status = models.CharField(max_length=7, choices=Mode.choices, null=False)

    class AppliesTo(models.TextChoices):
        PER_CABIN = "per_cabin", _("Per Cabin")
        PER_PAX = "per_pax", _("Per Pax")

    applies_to = models.CharField(max_length=9, choices=Mode.choices, null=False)
    is_active = models.BooleanField(default=True, db_default=True, null=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    ships = models.ManyToManyField('ships_cabins.Ship', related_name='ship_custom_costs', through='ShipCustomCost')

class ShipCustomCost(models.Model):
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.CASCADE, null=False)
    custom_cost = models.ForeignKey(CustomCost, on_delete=models.CASCADE, null=False)
    pk = models.CompositePrimaryKey("ship_id", "custom_cost_id")

class CabinCostCustom(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False)
    custom_cost = models.ForeignKey(CustomCost, on_delete=models.RESTRICT, null=False)
    value = models.DecimalField(max_digits=12, decimal_places=4)
    percent = models.DecimalField(max_digits=6, decimal_places=4)
    currency = models.CharField(max_length=3)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='cabin_cost_format_check'
            ),
            models.CheckConstraint(
                check=(models.Q(value__isnull=False) & models.Q(percent__isnull=True)) |
                      (models.Q(value__isnull=True) & models.Q(percent__isnull=False)),
                name='ck_custom_value'
            ),
            models.UniqueConstraint(
                fields=['sailing', 'cabin', 'custom_cost'],
                name='unique_sailing_cabin_custom_cost'
            )
        ]