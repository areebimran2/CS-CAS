from typing import Union

from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from selling.schemas import (
    BookingOut, BookingInFromHold, BookingInDirect,
    CancellationQuoteIn, CancellationQuoteOut,
    CancellationIn, CancellationOut,
)

router = Router(tags=['I3 + I4. Booking'])

@router.post('', response=BookingOut)
@requires('selling.book')
def create_booking(request, payload: Union[BookingInFromHold, BookingInDirect]):
    """
    Creates a booking either by converting a hold into a booking or directly. Stores a pricing snapshot.
    """

@router.get('/bookings', response=NinjaPaginationResponseSchema[BookingOut])
@requires('selling.view')
@paginate()
def list_bookings(request):
    """
    Returns a list of bookings.
    """

@router.get('/{booking_id}', response=BookingOut)
@requires('selling.view')
def get_booking(request, booking_id):
    """
    Returns the specified bookings details.
    """

@router.post('/{booking_id}/cancellation/quote', response=CancellationQuoteOut)
@requires('selling.view')
def cancellation_quote_booking(request, payload: CancellationQuoteIn, booking_id):
    """
    Computes the cancellation charge using the tier engine (days-out selects a tier; charge depends on tier type),
    using the booking's snapshot totals/CoS.
    """

@router.post('/{booking_id}/cancellation', response=CancellationOut)
@requires('selling.cancel')
def cancellation_booking(request, payload: CancellationIn, booking_id):
    """
    Cancels the specified booking.
    """