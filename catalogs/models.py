import pgtrigger

from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.functions import TxNow
from common.trigger_functions import set_updated_at

class Amenity(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(unique=True, null=False)
    is_active = models.BooleanField(db_default=True, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'amenities'
        triggers = [
            pgtrigger.Trigger(
                name='trg_amenities_updated',
                when=pgtrigger.Before,
                operation=pgtrigger.Update,
                level=pgtrigger.Row,
                func=set_updated_at(),
            )
        ]

class CabinCategory(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(unique=True, null=False)
    sort_order = models.IntegerField(db_default=100, null=False)
    is_active = models.BooleanField(db_default=True, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'cabin_categories'
        triggers = [
            pgtrigger.Trigger(
                name='trg_cabin_cat_updated',
                when=pgtrigger.Before,
                operation=pgtrigger.Update,
                level=pgtrigger.Row,
                func=set_updated_at(),
            )
        ]

class Setting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.JSONField(null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'settings'