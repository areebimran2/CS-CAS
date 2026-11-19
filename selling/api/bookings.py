import uuid
from typing import Annotated, Optional, Union

from ninja import Header, Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from pydantic import Field

from common.access import requires
from selling.schemas import (
    BookingFilter,
    BookingInDirect,
    BookingInFromHold,
    BookingOut,
    CancellationIn,
    CancellationOut,
    CancellationQuoteIn,
    CancellationQuoteOut,
)

router = Router(tags=['I3. Bookings & Cancellations'])

BookingIn = Annotated[Union[BookingInFromHold, BookingInDirect], Field(discriminator='mode')]


@router.get('', response=NinjaPaginationResponseSchema[BookingOut])
@requires('selling.view')
@paginate()
def list_bookings(request, filters: Query[BookingFilter]):
    """
    Returns bookings, newest first, filtered by sailing, cabin, seller, status or UC Ref.
    """


@router.post('', response=BookingOut)
@requires('selling.book')
def create_booking(request, payload: BookingIn,
                   idempotency_key: Optional[str] = Header(default=None, alias='Idempotency-Key')):
    """
    Books a cabin, either from a hold (`mode: from_hold`) or directly (`mode: direct`), and stores a snapshot of the
    pricing inputs. Responds 409 `CABIN_BOOKED` when the cabin is already booked and 409 `HOLD_EXISTS` when someone
    else holds it. Repeating a request with the same `Idempotency-Key` returns the first booking.
    """


@router.get('/{booking_id}', response=BookingOut)
@requires('selling.view')
def get_booking(request, booking_id: uuid.UUID):
    """
    Returns a booking with its pricing snapshot.
    """


@router.post('/{booking_id}/cancel/quote', response=CancellationQuoteOut)
@requires('selling.view')
def quote_booking_cancellation(request, payload: CancellationQuoteIn, booking_id: uuid.UUID):
    """
    Calculates the cancellation charge without cancelling: the days before departure select the policy's tier, which
    is applied to the booking's snapshot totals.
    """


@router.post('/{booking_id}/cancel', response=CancellationOut)
@requires('selling.cancel')
def cancel_booking(request, payload: CancellationIn, booking_id: uuid.UUID):
    """
    Cancels a booking with the charge the seller entered, records the calculation in the audit log, and emails Sales
    that the cabin is available again at its current price.
    """
