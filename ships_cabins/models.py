from django.db import models
from django.db.models.functions import Now
from django.contrib.postgres.functions import RandomUUID
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Ship(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    name = models.TextField(unique=True, null=False)
    operator = models.TextField()
    contact_person = models.TextField()
    address = models.JSONField()
    is_archived = models.BooleanField(default=False, db_default=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    amenities = models.ManyToManyField('catalogs.Amenity', related_name='ship_amenities', through='ShipAmenity')

class ShipCurrency(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, null=False)
    pk = models.CompositePrimaryKey("ship_id", "currency")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='ship_currency_format_check'
            )
        ]

class ShipAmenity(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    amenity = models.ForeignKey('catalogs.Amenity', on_delete=models.RESTRICT)
    pk = models.CompositePrimaryKey("ship_id", "amenity_id")

class Cabin(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    ship = models.ForeignKey(Ship, on_delete=models.RESTRICT, null=False)
    name = models.TextField(null=False)
    number = models.TextField(null=False)
    deck = models.TextField()
    category = models.ForeignKey('catalogs.CabinCategory', on_delete=models.RESTRICT, null=False)
    is_archived = models.BooleanField(default=False, db_default=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ship', 'number'],
                name='unique_ship_number'
            ),
        ]

class CabinMap(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    ship = models.ForeignKey(Ship, on_delete=models.RESTRICT, null=False)
    version = models.IntegerField(null=False)

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        ARCHIVED = "archived", _("Archived")

    status = models.CharField(default=Status.DRAFT, db_default=Status.DRAFT,
                              max_length=8, choices=Status.choices, null=False)
    svg_url = models.TextField()
    raster_url = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ship', 'version'],
                name='unique_ship_version'
            ),
        ]

class CabinMapZone(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    map = models.ForeignKey(CabinMap, on_delete=models.CASCADE, null=False)
    cabin = models.ForeignKey(Cabin, on_delete=models.RESTRICT, null=False)
    polygon = models.JSONField(null=False)