from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.functions import TxNow
from common.triggers import set_updated_at_trg

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

class Setting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.JSONField(null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'settings'