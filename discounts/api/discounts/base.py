from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from discounts.schemas import *

router = Router(tags=['J1. Discounts'])


@router.get('', response=NinjaPaginationResponseSchema[DiscountOut])
@paginate()
def list_discounts(request):
    """
    Returns a list of discount "summaries".
    """

@router.post('', response=DiscountOut)
def create_discount(request, payload: DiscountIn):
    """
    Creates a new discount and its targets.
    """

@router.get('/{discount_id}', response=DiscountOut)
def get_discount(request, discount_id):
    """
    Returns a single discount by id.
    """

@router.put('/{discount_id}', response=DiscountOut)
def update_discount(request, payload: DiscountIn, discount_id):
    """
    Updates discount by replacing discount fields and targets.
    """

@router.post('/{discount_id}/activate', response=DiscountActivateOut)
def activate_discount(request, discount_id):
    """
    Forces a discount into "active" state (admin override).
    """

@router.post('/{discount_id}/deactivate', response=DiscountDeactivateOut)
def deactivate_discount(request, discount_id):
    """
    Forces a discount out of activation early.
    """