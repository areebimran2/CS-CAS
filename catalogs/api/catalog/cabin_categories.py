from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.schemas import *

router = Router(tags=['C2. Cabin Categories'])

@router.get('', response=NinjaPaginationResponseSchema[CabinCategoryOut])
@paginate()
def list_cabin_categories(request):
    """
    Returns a list of all valid cabin categories.
    """
    return CabinCategory.objects.all()

@router.post('', response=CabinCategoryOut)
def create_cabin_category(request, payload: CabinCategoryIn):
    """
    Creates a new cabin category.
    """
    cabin_category = CabinCategory.objects.create(**payload.dict())
    return cabin_category

@router.put('/{category_id}', response=CabinCategoryOut)
def update_cabin_category(request,  payload: PatchDict[CabinCategoryIn], category_id: str):
    """
    Updates an existing cabin category.
    """
    cabin_category = CabinCategory.objects.get(id=category_id)

    for attr, value in payload.items():
        setattr(cabin_category, attr, value)

    cabin_category.save()
    return cabin_category