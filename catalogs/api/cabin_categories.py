import uuid

from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.models import CabinCategory
from catalogs.schemas import CabinCategoryIn, CabinCategoryOut
from catalogs.services import cabin_categories as service
from common.access import requires

router = Router(tags=['C2. Cabin Categories'])


@router.get('', response=NinjaPaginationResponseSchema[CabinCategoryOut])
@requires('catalogs.view')
@paginate()
def list_cabin_categories(request):
    """
    Returns a list of all valid cabin categories.
    """
    return CabinCategory.objects.all()


@router.post('', response=CabinCategoryOut)
@requires('catalogs.create')
def create_cabin_category(request, payload: CabinCategoryIn):
    """
    Creates a new cabin category.
    """
    return service.create_cabin_category(**payload.dict())


@router.get('/{category_id}', response=CabinCategoryOut)
@requires('catalogs.view')
def get_cabin_category(request, category_id: uuid.UUID):
    """
    Returns a cabin category.
    """


@router.put('/{category_id}', response=CabinCategoryOut)
@requires('catalogs.edit')
def update_cabin_category(request,  payload: PatchDict[CabinCategoryIn], category_id: uuid.UUID):
    """
    Updates an existing cabin category.
    """
    cabin_category = get_object_or_404(CabinCategory, id=category_id)
    return service.update_cabin_category(cabin_category, payload)


@router.delete('/{category_id}', response={204: None})
@requires('catalogs.delete')
def delete_cabin_category(request, category_id: uuid.UUID):
    """
    Deletes a cabin category that no cabins, pricing or discounts use. Otherwise responds 409 `IN_USE`;
    deactivate it instead.
    """
