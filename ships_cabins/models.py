from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.enums import MapStatus
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg

class Ship(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    operator = models.TextField(null=True)
    contact_person = models.TextField(null=True)
    address = models.JSONField(null=True)
    is_archived = models.BooleanField(db_default=False, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    amenities = models.ManyToManyField('catalogs.Amenity', related_name='ship_amenities', through='ShipAmenity')

    class Meta:
        db_table = 'ships'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='ships_name_key'
            )
        ]
        triggers = [
            set_updated_at_trg('trg_ships_updated'),
        ]

class ShipCurrency(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, db_index=False)
    currency = models.CharField(max_length=3, null=False, db_index=False)
    pk = models.CompositePrimaryKey('ship_id', 'currency')

    class Meta:
        db_table = 'ship_currencies'
        constraints = [
            models.CheckConstraint(
                check=models.Q(currency__regex=r'^[A-Z]{3}$'),
                name='ship_currencies_currency_check'
            )
        ]

class ShipAmenity(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, db_index=False)
    amenity = models.ForeignKey('catalogs.Amenity', on_delete=models.RESTRICT, db_index=False)
    pk = models.CompositePrimaryKey('ship_id', 'amenity_id')

    class Meta:
        db_table = 'ship_amenities'

class Cabin(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    number = models.TextField(null=False)
    deck = models.TextField(null=True)
    is_archived = models.BooleanField(db_default=False, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    ship = models.ForeignKey(Ship, on_delete=models.RESTRICT, null=False, db_index=False)
    category = models.ForeignKey('catalogs.CabinCategory', on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'cabins'
        constraints = [
            models.UniqueConstraint(
                fields=['ship', 'number'],
                name='cabins_ship_id_number_key'
            )
        ]
        indexes = [
            models.Index(fields=['ship'], name='idx_cabins_ship')
        ]
        triggers = [
            set_updated_at_trg('trg_cabins_updated'),
        ]

class CabinMap(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    version = models.IntegerField(null=False)
    status = PostgresEnumField('map_status', db_default=MapStatus.DRAFT, choices=MapStatus.choices, null=False)
    svg_url = models.TextField(null=True)
    raster_url = models.TextField(null=True)
    notes = models.TextField(null=True)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    ship = models.ForeignKey(Ship, on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'cabin_maps'
        constraints = [
            models.UniqueConstraint(
                fields=['ship', 'version'],
                name='cabin_maps_ship_id_version_key'
            ),
        ]
        triggers = [
            set_updated_at_trg('trg_cabin_maps_updated'),
        ]

class CabinMapZone(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    map = models.ForeignKey(CabinMap, on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey(Cabin, on_delete=models.RESTRICT, null=False, db_index=False)
    polygon = models.JSONField(null=False)

    class Meta:
        db_table = 'cabin_zones'
        indexes = [
            models.Index(fields=['map'], name='idx_cabin_zones_map')
        ]