import uuid

from django.shortcuts import get_object_or_404
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
    return Amenity.objects.all()

@router.post('', response=AmenityOut)
def create_amenity(request, payload: AmenityIn):
    """
    Creates a new amenity.
    """
    amenity = Amenity.objects.create(**payload.dict())
    return amenity


@router.put('/{amenity_id}', response=AmenityOut)
def update_amenity(request, payload: PatchDict[AmenityIn], amenity_id: uuid.UUID):
    """
    Update an existing amenity.
    """
    amenity = get_object_or_404(Amenity, id=amenity_id)

    for attr, value in payload.items():
        setattr(amenity, attr, value)

    amenity.save()
    return amenity
