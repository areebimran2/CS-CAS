from django.db import models
from django.db.models.functions import Now
from django.contrib.postgres.functions import RandomUUID
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class ReserveSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    max_hold_minutes = models.IntegerField(default=2880, db_default=2880, null=False)
    reminder_scheduled_minutes = ArrayField(base_field=models.IntegerField(), default=list,
                                            db_default='{2880, 1440}', null=False)
    allow_extensions = models.BooleanField(default=True, db_default=True, null=False)
    max_extensions = models.IntegerField(default=1, db_default=1, null=False)
    extension_minutes = models.IntegerField(default=1440, db_default=1440, null=False)
    # created_by = models.ForeignKey('myadmin.User')
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

class Hold(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False)
    uc_ref = models.TextField(null=False)
    # user = models.ForeignKey('myadmin.User', on_delete=models.RESTRICT, null=False)
    expires_at = models.DateTimeField(null=False)

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        RELEASED = "released", _("Released")
        EXPIRED = "expired", _("Expired")
        CONVERTED = "converted", _("Converted")

    status = models.CharField(default=Status.ACTIVE, db_default=Status.ACTIVE,
                              max_length=9, choices=Status.choices, null=False)
    idempotency_key = models.TextField(unique=True)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

class ReleaseRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    hold = models.ForeignKey(Hold, on_delete=models.CASCADE, null=False)
    # requested_by = models.ForeignKey('myadmin.User', on_delete=models.RESTRICT, null=False)
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False)
    uc_ref = models.TextField(null=False)
    # user = models.ForeignKey('myadmin.User', on_delete=models.RESTRICT, null=False)
    snapshot = models.JSONField(null=False)
    idempotency_key = models.TextField(unique=True)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

class CancellationPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    name = models.TextField(null=False)
    non_refundable = models.BooleanField(default=False, db_default=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now(), null=False)

class CancellationPolicyTier(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    policy = models.ForeignKey(CancellationPolicy, on_delete=models.CASCADE, null=False)
    min_days = models.IntegerField(null=False)
    max_days = models.IntegerField(null=False)

    class ChargeType(models.TextChoices):
        PERCENT_TOTAL = "percent_total", _("Percent Total")
        PERCENT_COS = "percent_cos", _("Percent COS")
        FIXED_AMOUNT = "fixed_amount", _("Fixed Amount")

    charge_type = models.CharField(max_length=13, choices=ChargeType.choices, null=False)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_days__lte=models.F('max_days')),
                name='ck_days_order'
            )
        ]