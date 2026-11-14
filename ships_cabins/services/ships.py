from django.db import transaction

from catalogs.models import Amenity
from common.services import update_instance
from common.storage import delete_file, upload_file
from ships_cabins.models import Ship, ShipAmenity, ShipCurrency, ShipPhoto


@transaction.atomic
def create_ship(*, currencies, amenities=(), new_amenities=(), **fields) -> Ship:
    """Create a ship with its currencies and amenities. `new_amenities` are names added to the master list."""
    ship = Ship.objects.create(**fields)
    _set_currencies_and_amenities(ship, currencies, amenities, new_amenities)
    return ship


@transaction.atomic
def replace_ship(ship: Ship, *, currencies, amenities=(), new_amenities=(), **fields) -> Ship:
    """Replace the ship's details, currencies and amenities with the given ones."""
    ship.shipcurrency_set.all().delete()
    ship.shipamenity_set.all().delete()
    _set_currencies_and_amenities(ship, currencies, amenities, new_amenities)
    return update_instance(ship, fields)


@transaction.atomic
def add_ship_photos(ship: Ship, files) -> list[ShipPhoto]:
    # File type and size checks are not implemented yet (spec D1: JPG/PNG/SVG/WEBP).
    urls = [upload_file(file, folder=f'ships/{ship.id}') for file in files]
    return ShipPhoto.objects.bulk_create([ShipPhoto(ship=ship, url=url) for url in urls])


@transaction.atomic
def reorder_ship_photos(ship: Ship, sort_orders: dict) -> list[ShipPhoto]:
    """Set each photo's position from `sort_orders` (photo id -> sort order). Photos not listed keep theirs."""
    photos = list(ship.shipphoto_set.all())
    for photo in photos:
        photo.sort_order = sort_orders.get(photo.id, photo.sort_order)
    ShipPhoto.objects.bulk_update(photos, fields=['sort_order'])
    return sorted(photos, key=lambda photo: (photo.sort_order, photo.created_at))


@transaction.atomic
def delete_ship_photo(photo: ShipPhoto) -> None:
    photo.delete()
    # Remove the stored file only once the row is gone for good, so a failed delete never loses the file.
    transaction.on_commit(lambda: delete_file(photo.url))


def _set_currencies_and_amenities(ship, currencies, amenity_ids, new_amenity_names):
    ShipCurrency.objects.bulk_create([ShipCurrency(ship=ship, currency=currency) for currency in currencies])

    Amenity.objects.bulk_create([Amenity(name=name) for name in new_amenity_names],
                                ignore_conflicts=True, unique_fields=['name'])
    new_ids = Amenity.objects.filter(name__in=new_amenity_names).values_list('id', flat=True)
    ShipAmenity.objects.bulk_create([ShipAmenity(ship=ship, amenity_id=amenity_id)
                                     for amenity_id in {*amenity_ids, *new_ids}], ignore_conflicts=True)
