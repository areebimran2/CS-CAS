import uuid
from typing import List

from django.shortcuts import get_object_or_404
from ninja import File, Query, Router, Status
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
    ShipFilter,
    ShipIn,
    ShipListOut,
    ShipOut,
)
from ships_cabins.services import ships as service

router = Router(tags=['D1. Ships'])


@router.get('', response=NinjaPaginationResponseSchema[ShipListOut])
@requires('ships.view')
@paginate()
def list_ships(request, filters: Query[ShipFilter]):
    """
    Returns ships ordered by name. By default only current ships; `?archived=true` lists archived ones and
    `?archived=all` both. `?search=` matches the name or operator.
    """
    return filters.filter(service.ships_with_summary())


@router.post('', response=ShipOut)
@requires('ships.create')
def create_ship(request, payload: ShipIn):
    """
    Creates a ship with its currencies (at least one) and amenities. `new_amenities` are names added to the amenity
    master list, matching existing ones regardless of case.
    """
    return service.create_ship(**payload.dict())


@router.get('/{ship_id}', response=ShipDetailOut)
@requires('ships.view')
def get_ship(request, ship_id: uuid.UUID):
    """
    Returns a ship with its currencies, amenities, photos, number of current cabins and active cabin map version.
    """
    return get_object_or_404(service.ships_with_summary(), id=ship_id)


@router.put('/{ship_id}', response=ShipOut)
@requires('ships.edit')
def replace_ship(request, payload: ShipIn, ship_id: uuid.UUID):
    """
    Replaces a ship's details, currencies and amenities. Send the complete ship: optional fields that are left out
    are cleared.
    """
    return service.replace_ship(get_object_or_404(Ship, id=ship_id), **payload.dict())


@router.post('/{ship_id}/archive', response=ShipOut)
@requires('ships.edit')
def archive_ship(request, ship_id: uuid.UUID):
    """
    Archives a ship, which hides it from the default ship list. Its cabins and history are kept.
    """
    return service.set_ship_archived(get_object_or_404(Ship, id=ship_id), True)


@router.post('/{ship_id}/unarchive', response=ShipOut)
@requires('ships.edit')
def unarchive_ship(request, ship_id: uuid.UUID):
    """
    Restores an archived ship.
    """
    return service.set_ship_archived(get_object_or_404(Ship, id=ship_id), False)


@router.delete('/{ship_id}', response={204: None})
@requires('ships.delete')
def delete_ship(request, ship_id: uuid.UUID):
    """
    Deletes a ship that nothing refers to: no cabins, cabin maps, seasons, sailings or pricing. Otherwise responds
    409 `IN_USE`; archive the ship instead.
    """
    service.delete_ship(get_object_or_404(Ship, id=ship_id))
    return Status(204, None)


# -- Photo gallery

@router.post('/{ship_id}/photos/upload-urls')
@requires('ships.edit')
def upload_ship_photo_urls(request, ship_id: uuid.UUID, payload: PhotoUploadUrlsIn):
    """
    Generate presigned URLs for the client to upload photos directly to object storage.
    """


@router.post('/{ship_id}/photos', response=ListPhotoOut)
@requires('ships.edit')
def upload_ship_photo(request, files: File[List[UploadedFile]], ship_id: uuid.UUID):
    """
    Upload a photo to the ship gallery.
    """
    return {'photos': service.add_ship_photos(get_object_or_404(Ship, id=ship_id), files)}


@router.post('/{ship_id}/photos/reorder', response=ListPhotoOut)
@requires('ships.edit')
def reorder_ship_photos(request, payload: ReorderPhotoIn, ship_id: uuid.UUID):
    """
    Update the sort order of the ships' gallery.
    """
    sort_orders = {item.id: item.sort_order for item in payload.order}
    return {'photos': service.reorder_ship_photos(get_object_or_404(Ship, id=ship_id), sort_orders)}


@router.delete('/{ship_id}/photos/{photo_id}', response={204: None})
@requires('ships.edit')
def delete_ship_photo(request, photo_id: uuid.UUID, ship_id: uuid.UUID):
    """
    Remove a specific photo from the ship gallery.
    """
    service.delete_ship_photo(get_object_or_404(ShipPhoto, ship_id=ship_id, id=photo_id))
    return Status(204, None)
