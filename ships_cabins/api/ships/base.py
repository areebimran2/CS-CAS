from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.files import UploadedFile
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.storage import upload_file, delete_file
from ships_cabins.models import Ship, ShipPhoto
from ships_cabins.schemas import (
    ShipOut, ShipDetailOut, ShipIn, ShipListOut, ListPhotoOut, ReorderPhotoIn, PhotoUploadUrlsIn,
)
from ships_cabins.services.ships import create_ship_joins

router = Router(tags=['D1. Ships'])


@router.get('', response=NinjaPaginationResponseSchema[ShipListOut])
@paginate()
def list_ships(request):
    """
    Returns a list of active ships.
    """
    return Ship.objects.all()


@router.post('', response=ShipOut)
def create_ship(request, payload: ShipIn):
    """
    Create a new ship with  its currencies, and optionally amenities.
    """
    payload_dict = payload.dict(exclude=['currencies', 'amenities', 'new_amenities'], exclude_unset=True)
    ship = Ship.objects.create(**payload_dict)

    create_ship_joins(ship, payload.currencies, payload.amenities, payload.new_amenities)

    return ship


@router.get('/{ship_id}', response=ShipDetailOut)
def get_ship(request, ship_id):
    """
    Retrieve a single ship with all its currencies, amenities, photos, and summary count
    """
    ship = get_object_or_404(Ship, id=ship_id)
    return ship


@router.put('/{ship_id}', response=ShipOut)
def update_ship(request, payload: ShipIn, ship_id):
    """
    FUll replacement of a ship's metadata, currencies, and amenities. The client sends the complete desired state;
    omitted optional fields are set to `null` or made empty.
    """
    ship = get_object_or_404(Ship, id=ship_id)

    data = payload.dict(exclude=['currencies', 'amenities', 'new_amenities'], exclude_unset=True)

    for attr, value in data.items():
        setattr(ship, attr, value)

    ship.shipcurrency_set.all().delete()
    ship.shipamenity_set.all().delete()

    create_ship_joins(ship, payload.currencies, payload.amenities, payload.new_amenities)

    ship.save()
    return ship


@router.post('/{ship_id}/photos/upload-urls')
def upload_ship_photo_urls(request, ship_id, payload: PhotoUploadUrlsIn):
    """
    Generate presigned URLs for the client to upload photos directly to object storage.
    """


@router.post('/{ship_id}/photos', response=ListPhotoOut)
def upload_ship_photo(request, files: File[List[UploadedFile]], ship_id):
    """
    Upload a photo to the ship gallery.
    """
    ship = get_object_or_404(Ship, id=ship_id)

    photos = []

    # ALLOWED = {"image/jpeg", "image/png", "image/svg+xml", "image/webp"}
    # MAX_SIZE = 10 * 1024 * 1024  # 10 MB

    for file in files:
        # if file.content_type not in ALLOWED:
        #     ...  # return 422
        # if file.size > MAX_SIZE:
        #     ...  # return 422

        url = upload_file(file, folder=f'ships/{ship.id}')
        photos.append(ShipPhoto(url=url, ship=ship))

    photo_objs = ShipPhoto.objects.bulk_create(photos)

    return {
        'photos': photo_objs
    }


@router.post('/{ship_id}/photos/reorder', response=ListPhotoOut)
def reorder_ship_photos(request, payload: ReorderPhotoIn, ship_id):
    """
    Update the sort order of the ships' gallery.
    """
    ship = get_object_or_404(Ship, id=ship_id)

    # Map photo.id → sort_order from the request
    order_map = {item.id: item.sort_order for item in payload.order}

    # Fetch existing photos, set new sort_order, bulk update
    photos = list(ship.shipphoto_set.all())
    for photo in photos:
        photo.sort_order = order_map.get(photo.id, photo.sort_order)  # default to existing sort_order if not in request

    updated_photos = ShipPhoto.objects.bulk_update(photos, fields=['sort_order'])

    return {
        'photos': updated_photos
    }


@router.delete('/{ship_id}/photos/{photo_id}', response={204: None})
def delete_ship_photo(request, photo_id, ship_id):
    """
    Remove a specific photo from the ship gallery.
    """
    ship = get_object_or_404(Ship, id=ship_id)
    photo = get_object_or_404(ShipPhoto, ship=ship, id=photo_id)

    delete_file(photo.url)
    photo.delete()

    return 204, None
