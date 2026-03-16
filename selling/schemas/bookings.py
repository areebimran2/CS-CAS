import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Literal, Dict

from ninja import Schema, ModelSchema

from catalogs.schemas.cancellation_policies import MoneyOut
from selling.models import Booking


class BookingStatus(str, Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'

class OccupancyMode(str, Enum):
    TWO_PAX = '2-pax'
    SINGLE = 'single'


class BookingOut(ModelSchema):
    status: BookingStatus

    class Meta:
        model = Booking
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'idempotency_key', 'status']

class BookingInFromHold(Schema):
    mode: Literal['from_hold']
    hold: uuid.UUID
    occupancy_mode: OccupancyMode
    acknowledge_policy: bool
    notes: Optional[str] = None

class BookingInDirect(Schema):
    mode: Literal['direct']
    sailing: uuid.UUID
    cabin: uuid.UUID
    uc_ref: str
    occupancy_mode: OccupancyMode
    acknowledge_policy: bool
    notes: Optional[str] = None

class CancellationQuoteIn(Schema):
    policy: uuid.UUID

class CancellationQuoteOut(Schema):
    booking: uuid.UUID
    policy: uuid.UUID
    tier: uuid.UUID
    days_out: uuid.UUID
    charge: MoneyOut
    calculation: Dict
    clamped: bool

class CancellationIn(Schema):
    policy: uuid.UUID
    charge: MoneyOut
    reason: Optional[str] = None

class CancellationOut(ModelSchema):
    status: BookingStatus
    cancelled_at: datetime

    class Meta:
        model = Booking
        fields = ['id']

