from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.schemas import *

router = Router(tags=['C3. Custom Costs'])


@router.get('', response=NinjaPaginationResponseSchema[CustomCostOut])
@paginate()
def list_custom_costs(request):
    """
    Returns a list of all configurable cost types used for pricing.
    """


@router.post('', response=CustomCostOut)
def create_custom_cost(request, payload: CustomCostIn):
    """
    Create a configurable cost type.
    """


@router.put('/{cost_id}', response=CustomCostOut)
def update_custom_cost(request, payload: PatchDict[CustomCostIn], cost_id: str):
    """
    Update an existing cost type.
    """
