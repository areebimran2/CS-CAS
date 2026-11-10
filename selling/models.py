from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.enums import HoldStatus, BookingStatus
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg

# Reserve settings and cancellation policies are admin-managed policies and live in catalogs.models.

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