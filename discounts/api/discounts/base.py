from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from discounts.schemas import (
    DiscountOut, DiscountIn, DiscountActivateOut, DiscountDeactivateOut,
)

router = Router(tags=['J1. Discounts'])


@router.get('', response=NinjaPaginationResponseSchema[DiscountOut])
@requires('discounts.view')
@paginate()
def list_discounts(request):
    """
    Returns a list of discount "summaries".
    """

@router.post('', response=DiscountOut)
@requires('discounts.create')
def create_discount(request, payload: DiscountIn):
    """
    Creates a new discount and its targets.
    """

@router.get('/{discount_id}', response=DiscountOut)
@requires('discounts.view')
def get_discount(request, discount_id):
    """
    Returns a single discount by id.
    """

@router.put('/{discount_id}', response=DiscountOut)
@requires('discounts.edit')
def update_discount(request, payload: DiscountIn, discount_id):
    """
    Updates discount by replacing discount fields and targets.
    """

@router.post('/{discount_id}/activate', response=DiscountActivateOut)
@requires('discounts.activate')
def activate_discount(request, discount_id):
    """
    Forces a discount into "active" state (admin override).
    """

@router.post('/{discount_id}/deactivate', response=DiscountDeactivateOut)
@requires('discounts.activate')
def deactivate_discount(request, discount_id):
    """
    Forces a discount out of activation early.
    """