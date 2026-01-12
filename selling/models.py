from django.db import models
from django.contrib.postgres.functions import RandomUUID
from django.contrib.postgres.fields import ArrayField

from common.enums import HoldStatus, BookingStatus, CancellationChargeType
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg

class ReserveSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID, db_default=RandomUUID())
    max_hold_minutes = models.IntegerField(db_default=2880, null=False) # -- e.g., 48h
    reminder_scheduled_minutes = ArrayField(base_field=models.IntegerField(), db_default='{2880, 1440}', null=False) # -- 2d,1d before
    allow_extensions = models.BooleanField(db_default=True, null=False)
    max_extensions = models.IntegerField(db_default=1, null=False)
    extension_minutes = models.IntegerField(db_default=1440, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    created_by = models.ForeignKey('myauth.User', on_delete=models.DO_NOTHING, null=True,
                                   db_index=False, db_column='created_by')

    class Meta:
        db_table = 'reserve_settings'

class Hold(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    uc_ref = models.TextField(null=False)
    expires_at = models.DateTimeField(null=False)
    status = PostgresEnumField('hold_status', db_default=HoldStatus.ACTIVE, choices=HoldStatus.choices, null=False)
    idempotency_key = models.TextField(null=True)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    user = models.ForeignKey('myauth.User', on_delete=models.RESTRICT, null=False, db_index=False)
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'holds'
        constraints = [
            models.UniqueConstraint(
                fields=['idempotency_key'],
                name='holds_idempotency_key_key',
            ),
            # -- Only one ACTIVE hold per (sailing,cabin)
            models.UniqueConstraint(
                fields=['sailing', 'cabin'],
                condition=models.Q(status=HoldStatus.ACTIVE),
                name='uidx_holds_active',
            ),
        ]
        triggers = [
            set_updated_at_trg('trg_holds_updated'),
        ]



class ReleaseRequest(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    reason = models.TextField(null=True)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    hold = models.ForeignKey(Hold, on_delete=models.CASCADE, null=False, db_index=False)
    requested_by = models.ForeignKey('myauth.User', on_delete=models.RESTRICT, null=False,
                                     db_index=False, db_column='requested_by')

    class Meta:
        db_table = 'release_requests'

class Booking(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    uc_ref = models.TextField(null=False)
    snapshot = models.JSONField(null=False)
    status = PostgresEnumField('booking_status', db_default=BookingStatus.ACTIVE, null=False)
    idempotency_key = models.TextField(null=True)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=False, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.RESTRICT, null=False, db_index=False)
    user = models.ForeignKey('myauth.User', on_delete=models.RESTRICT, null=False, db_index=False)

    class Meta:
        db_table = 'bookings'
        constraints = [
            models.UniqueConstraint(
                fields=['idempotency_key'],
                name='bookings_idempotency_key_key',
            ),
            # -- Only one ACTIVE booking per (sailing,cabin)
            models.UniqueConstraint(
                fields=['sailing', 'cabin'],
                condition=models.Q(status=BookingStatus.ACTIVE),
                name='uidx_bookings_active',
            ),
        ]
        triggers = [
            set_updated_at_trg('trg_bookings_updated'),
        ]


class CancellationPolicy(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    non_refundable = models.BooleanField(db_default=False, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'cancellation_policies'

class CancellationPolicyTier(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    min_days = models.IntegerField(null=False)
    max_days = models.IntegerField(null=False)
    charge_type = PostgresEnumField('cancellation_charge_type', choices=CancellationChargeType.choices, null=False)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=False)

    policy = models.ForeignKey(CancellationPolicy, on_delete=models.CASCADE, null=False, db_index=False)

    class Meta:
        db_table = 'cancellation_policy_tiers'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(min_days__lte=models.F('max_days')),
                name='ck_days_order'
            )
        ]