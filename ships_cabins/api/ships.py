from typing import List

from django.shortcuts import get_object_or_404
from ninja import File, Router, Status
from ninja.files import UploadedFile
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from ships_cabins.models import Ship, ShipPhoto
from ships_cabins.schemas import (
    ListPhotoOut,
    PhotoUploadUrlsIn,
    ReorderPhotoIn,
    ShipDetailOut,
    ShipIn,
    ShipListOut,
    ShipOut,
)
from ships_cabins.services import ships as service

router = Router(tags=['D1. Ships'])


@router.get('', response=NinjaPaginationResponseSchema[ShipListOut])
@requires('ships.view')
@paginate()
def list_ships(request):
    """
    Returns a list of active ships.
    """
    return Ship.objects.all()


@router.post('', response=ShipOut)
@requires('ships.create')
def create_ship(request, payload: ShipIn):
    """
    Create a new ship with  its currencies, and optionally amenities.
    """
    return service.create_ship(**payload.dict(exclude_unset=True))


@router.get('/{ship_id}', response=ShipDetailOut)
@requires('ships.view')
def get_ship(request, ship_id):
    """
    Retrieve a single ship with all its currencies, amenities, photos, and summary count
    """
    ship = get_object_or_404(Ship, id=ship_id)
    return ship


@router.put('/{ship_id}', response=ShipOut)
@requires('ships.edit')
def update_ship(request, payload: ShipIn, ship_id):
    """
    FUll replacement of a ship's metadata, currencies, and amenities. The client sends the complete desired state;
    omitted optional fields are set to `null` or made empty.
    """
    return service.replace_ship(get_object_or_404(Ship, id=ship_id), **payload.dict(exclude_unset=True))


@router.post('/{ship_id}/photos/upload-urls')
@requires('ships.edit')
def upload_ship_photo_urls(request, ship_id, payload: PhotoUploadUrlsIn):
    """
    Generate presigned URLs for the client to upload photos directly to object storage.
    """


@router.post('/{ship_id}/photos', response=ListPhotoOut)
@requires('ships.edit')
def upload_ship_photo(request, files: File[List[UploadedFile]], ship_id):
    """
    Upload a photo to the ship gallery.
    """
    return {'photos': service.add_ship_photos(get_object_or_404(Ship, id=ship_id), files)}


@router.post('/{ship_id}/photos/reorder', response=ListPhotoOut)
@requires('ships.edit')
def reorder_ship_photos(request, payload: ReorderPhotoIn, ship_id):
    """
    Update the sort order of the ships' gallery.
    """
    sort_orders = {item.id: item.sort_order for item in payload.order}
    return {'photos': service.reorder_ship_photos(get_object_or_404(Ship, id=ship_id), sort_orders)}


@router.delete('/{ship_id}/photos/{photo_id}', response={204: None})
@requires('ships.edit')
def delete_ship_photo(request, photo_id, ship_id):
    """
    Remove a specific photo from the ship gallery.
    """
    service.delete_ship_photo(get_object_or_404(ShipPhoto, ship_id=ship_id, id=photo_id))
    return Status(204, None)
