from django.db import models
from django.db.models.functions import Now
from django.contrib.postgres.functions import RandomUUID
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Season(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    name = models.TextField(unique=True, null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    default_margin_b2b = models.DecimalField(max_digits=6, decimal_places=4, null=False)
    default_margin_b2c = models.DecimalField(max_digits=6, decimal_places=4, null=False)
    is_archived = models.BooleanField(default=False, db_default=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    ships = models.ManyToManyField('ships_cabins.Ship', related_name='season_ships', through='SeasonShip')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lte=models.F('end_date')),
                name='season_nonempty'
            )
        ]

class SeasonShip(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=False)
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.RESTRICT, null=False)
    pk = models.CompositePrimaryKey("season_id", "ship_id")

class Sailing(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    season = models.ForeignKey(Season, on_delete=models.RESTRICT, null=False)
    ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.RESTRICT, null=False)
    route = models.ForeignKey('routes.Route', on_delete=models.SET_NULL, null=True)
    departure_date = models.DateField(null=False)
    nights = models.IntegerField(null=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(nights__gt=0),
                name='nights_nonempty'
            )
        ]

