import uuid
from typing import Optional

from ninja import ModelSchema, Schema

from common.enums import CabinAvailability
from selling.models import Booking, Hold


class HoldAvailabilityOut(ModelSchema):
    class Meta:
        model = Hold
        fields = ['id', 'uc_ref', 'expires_at']


class BookingAvailabilityOut(ModelSchema):
    class Meta:
        model = Booking
        fields = ['id', 'uc_ref']


class CabinAvailabilityOut(Schema):
    cabin_id: uuid.UUID
    status: CabinAvailability
    hold: Optional[HoldAvailabilityOut] = None
    booking: Optional[BookingAvailabilityOut] = None
