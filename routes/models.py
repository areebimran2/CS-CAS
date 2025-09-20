from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.functions import TxNow
from common.triggers import set_updated_at_trg

class Route(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=True)
    notes = models.TextField(null=True)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'routes'
        triggers = [
            set_updated_at_trg('trg_routes_updated'),
        ]

class RouteLeg(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    seq = models.IntegerField(null=False)
    place_id = models.TextField(null=False)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    tz = models.TextField(null=True)

    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False, db_index=False)

    class Meta:
        db_table = 'route_legs'
        constraints = [
            models.UniqueConstraint(
                fields=['route', 'seq'],
                name='route_legs_route_id_seq_key'
            ),
        ]