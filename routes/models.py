from django.db import models

from django.contrib.postgres.functions import RandomUUID
from django.utils import timezone

class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID)
    name = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False)

class RouteLeg(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False)
    seq = models.IntegerField(null=False)
    place_id = models.TextField(null=False)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    tz = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['route', 'seq'],
                name='unique_route_seq'
            ),
        ]