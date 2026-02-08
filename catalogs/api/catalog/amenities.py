from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.schemas import *

router = Router(tags=['C1. Amenities'])


@router.get('', response=NinjaPaginationResponseSchema[AmenityOut])
@paginate()
def list_amenities(request):
    """
    Returns a list of available amenities in the system.
    """


@router.post('', response=AmenityOut)
def create_amenity(request, payload: AmenityIn):
    """
    Creates a new amenity.
    """


@router.put('/{amenity_id}', response=AmenityOut)
def update_amenity(request, payload: PatchDict[AmenityIn], amenity_id: str):
    """
    Update an existing amenity.
    """
