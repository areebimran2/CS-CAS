from django.db import models

from django.contrib.postgres.functions import RandomUUID
from django.utils import timezone

class Amenity(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID)
    name = models.TextField(unique=True, null=False)
    is_active = models.BooleanField(default=True, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False)

class CabinCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID)
    name = models.TextField(unique=True, null=False)
    sort_order = models.IntegerField(default=100, null=False)
    is_active = models.BooleanField(default=True, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False)