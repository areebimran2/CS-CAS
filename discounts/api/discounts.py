import uuid

from ninja import Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from discounts.schemas import DiscountFilter, DiscountIn, DiscountOut

router = Router(tags=['J1. Discounts'])


@router.get('', response=NinjaPaginationResponseSchema[DiscountOut])
@requires('discounts.view')
@paginate()
def list_discounts(request, filters: Query[DiscountFilter]):
    """
    Returns discounts by start time, filtered by status or channel. `?search=` matches the name.
    """


@router.post('', response=DiscountOut)
@requires('discounts.create')
def create_discount(request, payload: DiscountIn):
    """
    Creates a scheduled discount with its targets. It becomes active at `starts_at` and ends at `ends_at`.
    """


@router.get('/{discount_id}', response=DiscountOut)
@requires('discounts.view')
def get_discount(request, discount_id: uuid.UUID):
    """
    Returns a discount with its targets.
    """


@router.put('/{discount_id}', response=DiscountOut)
@requires('discounts.edit')
def replace_discount(request, payload: DiscountIn, discount_id: uuid.UUID):
    """
    Replaces a discount's fields and targets.
    """


@router.post('/{discount_id}/activate', response=DiscountOut)
@requires('discounts.activate')
def activate_discount(request, discount_id: uuid.UUID):
    """
    Activates a scheduled discount now, before its start time, and notifies Sales.
    """


@router.post('/{discount_id}/deactivate', response=DiscountOut)
@requires('discounts.activate')
def deactivate_discount(request, discount_id: uuid.UUID):
    """
    Cancels a scheduled or active discount before its end time, and notifies Sales.
    """
