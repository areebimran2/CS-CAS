from django.db import models
from django.db.models import ExpressionWrapper
from django.db.models.functions import Now
from django.contrib.postgres.functions import RandomUUID
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Discount(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    name = models.TextField(null=False)

    class Kind(models.TextChoices):
        PERCENT = 'percent', _('Percent')
        FIXED = 'fixed', _('Fixed')

    kind = models.CharField(max_length=7, choices=Kind.choices, null=False)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=False)

    class Channel(models.TextChoices):
        B2B = 'b2b', _('B2B')
        B2C = 'b2c', _('B2C')
        BOTH = 'both', _('Both')

    channel = models.CharField(max_length=4, default=Channel.B2B, db_default=Channel.B2B,
                               choices=Channel.choices, null=False)
    starts_at = models.DateTimeField(null=False)
    ends_at = models.DateTimeField(null=False)
    min_margin_b2b = models.DecimalField(max_digits=6, decimal_places=4, default=0.05, db_default=0.05, null=False)
    min_margin_b2c = models.DecimalField(max_digits=6, decimal_places=4, default=0.10, db_default=0.10, null=False)

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Scheduled")
        ACTIVE = "active", _("Active")
        ENDED = "ended", _("Ended")
        CANCELLED = "cancelled", _("Cancelled")

    status = models.CharField(max_length=9, default=Status.SCHEDULED, db_default=Status.SCHEDULED,
                              choices=Status.choices, null=False)
    # created_by = models.ForeignKey('myadmin.User')
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

class DiscountTarget(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=False)
    target_kind =  models.TextField(null=False)
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE)
    category = models.ForeignKey('catalogs.CabinCategory', on_delete=models.CASCADE)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.CASCADE)
    pk = models.CompositePrimaryKey("discount_id", "target_kind")

    # The below is invalid DDL and also breaks referential integrity in the database. Nullable fields cannot be part of a primary key.
    # pk = models.CompositePrimaryKey("discount_id", "target_kind", COALESCE("sailing_id", RANDOM_UUID()))


    class Meta:
        constraints = [
            # This is logically equivalent to:
            # ((sailing_id IS NOT NULL)::int + (category_id IS NOT NULL)::int + (cabin_id IS NOT NULL)::int) = 1
            models.CheckConstraint(
                check=(models.Q(sailing__isnull=False, category__isnull=True, cabin__isnull=True) |
                       models.Q(sailing__isnull=True, category__isnull=False, cabin__isnull=True) |
                       models.Q(sailing__isnull=True, category__isnull=True, cabin__isnull=False)),
                name='ck_target_exactly_one'
            )
        ]

