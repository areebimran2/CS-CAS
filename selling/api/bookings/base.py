from typing import Union

from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from selling.schemas import *

router = Router(tags=['I3 + I4. Booking'])

@router.post('', response=BookingOut)
def create_booking(request, payload: Union[BookingInFromHold, BookingInDirect]):
    """
    Creates a booking either by converting a hold into a booking or directly. Stores a pricing snapshot.
    """

@router.get('/bookings', response=NinjaPaginationResponseSchema[BookingOut])
@paginate()
def list_bookings(request):
    """
    Returns a list of bookings.
    """

@router.get('/{booking_id}', response=BookingOut)
def get_booking(request, booking_id):
    """
    Returns the specified bookings details.
    """

@router.post('/{booking_id}/cancellation/quote', response=CancellationQuoteOut)
def cancellation_quote_booking(request, payload: CancellationQuoteIn, booking_id):
    """
    Computes the cancellation charge using the tier engine (days-out selects a tier; charge depends on tier type),
    using the booking's snapshot totals/CoS.
    """

@router.post('/{booking_id}/cancellation', response=CancellationOut)
def cancellation_booking(request, payload: CancellationIn, booking_id):
    """
    Cancels the specified booking.
    """