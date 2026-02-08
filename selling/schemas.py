import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Literal, Dict

from ninja import Schema, ModelSchema

from catalogs.schemas import MoneyOut
from selling.models import Hold, ReleaseRequest, Booking


class HoldStatus(str, Enum):
    ACTIVE = 'active'
    RELEASED = 'released'
    EXPIRED = 'expired'
    CONVERTED = 'converted'

class BookingStatus(str, Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'

class RequestStatus(str, Enum):
    APPROVED = 'approved'
    DENIED = 'denied'

class OccupancyMode(str, Enum):
    TWO_PAX = '2-pax'
    SINGLE = 'single'

class ZohoDetailsOut(Schema):
    deal: Any
    channel: Any
    agency: Any
    agent: Any
    contact: Any

class HoldOut(ModelSchema):
    status: HoldStatus

    class Meta:
        model = Hold
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'idempotency_key', 'status']

class HoldIn(Schema):
    sailing: uuid.UUID
    cabin: uuid.UUID
    uc_ref: str
    notes: Optional[str] = None

class HoldExtensionOut(ModelSchema):
    status: HoldStatus

    class Meta:
        model = Hold
        fields = ['id', 'expires_at']

class ReasonIn(Schema):
    reason: Optional[str] = None

class HoldReleaseOut(Schema):
    status: HoldStatus

    class Meta:
        model = Hold
        fields = ['id']

class ReleaseRequestOut(ModelSchema):
    class Meta:
        model = ReleaseRequest
        fields = '__all__'

class ReleaseRequestResult(ModelSchema):
    result: RequestStatus

    class Meta:
        model = ReleaseRequest
        fields = ['id']

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