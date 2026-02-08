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

@router.post('', response=CabinCategoryOut)
def create_cabin_category(request, payload: CabinCategoryIn):
    """
    Creates a new cabin category.
    """

@router.put('/{category_id}', response=CabinCategoryOut)
def update_cabin_category(request,  payload: PatchDict[CabinCategoryIn], category_id: str):
    """
    Updates an existing cabin category.
    """