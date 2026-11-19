import uuid

from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.models import CustomCost
from catalogs.schemas import CustomCostIn, CustomCostOut
from catalogs.services import custom_costs as service
from common.access import requires

router = Router(tags=['C3. Custom Costs'])


@router.get('', response=NinjaPaginationResponseSchema[CustomCostOut])
@requires('catalogs.view')
@paginate()
def list_custom_costs(request):
    """
    Returns a list of all configurable cost types used for pricing.
    """
    return CustomCost.objects.all()


@router.post('', response=CustomCostOut)
@requires('catalogs.create')
def create_custom_cost(request, payload: CustomCostIn):
    """
    Create a configurable cost type.
    """
    return service.create_custom_cost(**payload.dict())


@router.get('/{cost_id}', response=CustomCostOut)
@requires('catalogs.view')
def get_custom_cost(request, cost_id: uuid.UUID):
    """
    Returns a custom cost.
    """


@router.put('/{cost_id}', response=CustomCostOut)
@requires('catalogs.edit')
def update_custom_cost(request, payload: PatchDict[CustomCostIn], cost_id: uuid.UUID):
    """
    Update an existing cost type.
    """
    return service.update_custom_cost(get_object_or_404(CustomCost, id=cost_id), payload)


@router.delete('/{cost_id}', response={204: None})
@requires('catalogs.delete')
def delete_custom_cost(request, cost_id: uuid.UUID):
    """
    Deletes a custom cost that no ships or cabin pricing use. Otherwise responds 409 `IN_USE`;
    deactivate it instead.
    """
