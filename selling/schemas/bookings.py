import uuid
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from ninja import FilterSchema, Schema
from pydantic import Field

from common.enums import BookingStatus, CancellationChargeType, Occupancy
from common.schemas import Money, NonEmptyStr, OptionalStr


# -- Requests

class BookingInFromHold(Schema):
    """Converts one of the signed-in user's active holds into a booking."""
    mode: Literal['from_hold']
    hold_id: uuid.UUID
    occupancy: Occupancy
    acknowledge_policy: bool = Field(description='The seller confirmed the cancellation policy with the client')
    notes: OptionalStr = None


class BookingInDirect(Schema):
    """Books a free cabin without holding it first."""
    mode: Literal['direct']
    sailing_id: uuid.UUID
    cabin_id: uuid.UUID
    uc_ref: NonEmptyStr
    occupancy: Occupancy
    acknowledge_policy: bool = Field(description='The seller confirmed the cancellation policy with the client')
    notes: OptionalStr = None


class BookingFilter(FilterSchema):
    sailing_id: Optional[uuid.UUID] = None
    cabin_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    status: Optional[BookingStatus] = None
    uc_ref: Optional[str] = None


class CancellationQuoteIn(Schema):
    cancellation_policy_id: uuid.UUID


class CancellationIn(Schema):
    cancellation_policy_id: uuid.UUID
    charge: Money = Field(description='The amount the seller entered; must match the quote')
    reason: OptionalStr = None


# -- Responses

class BookingOut(Schema):
    id: uuid.UUID
    sailing_id: uuid.UUID
    cabin_id: uuid.UUID
    user_id: uuid.UUID
    uc_ref: str
    status: BookingStatus
    snapshot: Dict[str, Any] = Field(
        description='The pricing inputs at the time of booking: base, custom costs, margin, discount and FX mode',
    )
    created_at: datetime


class CancellationQuoteOut(Schema):
    booking_id: uuid.UUID
    cancellation_policy_id: uuid.UUID
    tier_id: uuid.UUID
    days_out: int
    charge_type: CancellationChargeType
    charge: Money
    calculation: Dict[str, Any] = Field(description='The inputs and steps of the tier calculation, for the audit log')
    clamped: bool = Field(description='The charge was limited to the booking total')


class CancellationOut(Schema):
    id: uuid.UUID
    status: BookingStatus
    charge: Money
    cancelled_at: datetime
