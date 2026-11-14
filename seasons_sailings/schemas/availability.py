import uuid
from enum import Enum
from typing import Optional

from ninja import ModelSchema, Schema

from selling.models import Booking, Hold


class CabinStatus(str, Enum):
    AVAILABLE = 'available'
    RESERVED = 'reserved'
    BOOKED = 'booked'


class HoldAvailabilityOut(ModelSchema):
    class Meta:
        model = Hold
        fields = ['id', 'uc_ref', 'expires_at']

class BookingAvailabilityOut(ModelSchema):
    class Meta:
        model = Booking
        fields = ['id', 'uc_ref']

class CabinAvailabilityOut(Schema):
    cabin: uuid.UUID
    status: CabinStatus
    hold: Optional[HoldAvailabilityOut] = None
    booking: Optional[BookingAvailabilityOut] = None

