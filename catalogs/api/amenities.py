import uuid

from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.models import Amenity
from catalogs.schemas import AmenityIn, AmenityOut
from catalogs.services import amenities as service
from common.access import requires

router = Router(tags=['C1. Amenities'])


@router.get('', response=NinjaPaginationResponseSchema[AmenityOut])
@requires('catalogs.view')
@paginate()
def list_amenities(request):
    """
    Returns a list of available amenities in the system.
    """
    return Amenity.objects.all()


@router.post('', response=AmenityOut)
@requires('catalogs.create')
def create_amenity(request, payload: AmenityIn):
    """
    Creates a new amenity.
    """
    return service.create_amenity(**payload.dict())


@router.put('/{amenity_id}', response=AmenityOut)
@requires('catalogs.edit')
def update_amenity(request, payload: PatchDict[AmenityIn], amenity_id: uuid.UUID):
    """
    Update an existing amenity.
    """
    amenity = get_object_or_404(Amenity, id=amenity_id)
    return service.update_amenity(amenity, payload)
