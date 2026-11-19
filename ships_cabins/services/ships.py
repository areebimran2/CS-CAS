from django.db import transaction
from django.db.models import Count, OuterRef, Q, Subquery

from catalogs.models import Amenity
from common.enums import MapStatus
from common.exceptions import ValidationFailedError
from common.services import delete_if_unused, update_instance
from common.storage import delete_file, upload_file
from ships_cabins.models import CabinMap, Ship, ShipAmenity, ShipCurrency, ShipPhoto


def ships_with_summary():
    """Ships with the counts shown in lists and on the detail page, computed in the same query."""
    active_map = CabinMap.objects.filter(ship=OuterRef('pk'), status=MapStatus.ACTIVE)
    return (
        Ship.objects
        .annotate(
            amenity_count=Count('amenities', filter=Q(amenities__is_active=True), distinct=True),
            cabin_count=Count('cabin', filter=Q(cabin__is_archived=False), distinct=True),
            photo_count=Count('shipphoto', distinct=True),
            active_map_version=Subquery(active_map.values('version')[:1]),
        )
        .prefetch_related('shipcurrency_set', 'amenities')
        .order_by('name')  # Django skips Meta.ordering in queries that aggregate, so repeat it here
    )


@transaction.atomic
def create_ship(*, currencies, amenity_ids=(), new_amenities=(), **fields) -> Ship:
    """Create a ship with its currencies and amenities. `new_amenities` are names added to the master list."""
    amenities = _amenities_to_attach(amenity_ids, new_amenities)
    ship = Ship.objects.create(**fields)
    _set_currencies(ship, currencies)
    ship.amenities.set(amenities)
    return ship


@transaction.atomic
def replace_ship(ship: Ship, *, currencies, amenity_ids=(), new_amenities=(), **fields) -> Ship:
    """Replace the ship's details, currencies and amenities. Fields that aren't given are cleared."""
    already_attached = set(ship.amenities.values_list('id', flat=True))
    amenities = _amenities_to_attach(amenity_ids, new_amenities, already_attached=already_attached)
    ship.shipcurrency_set.all().delete()
    _set_currencies(ship, currencies)
    ship.amenities.set(amenities)
    return update_instance(ship, fields)


@transaction.atomic
def set_ship_archived(ship: Ship, archived: bool) -> Ship:
    """Archive or restore a ship. Its cabins keep their own archived flags."""
    return update_instance(ship, {'is_archived': archived})


@transaction.atomic
def delete_ship(ship: Ship) -> None:
    """Delete a ship that nothing refers to, with its currencies, amenity links and photos."""
    photo_urls = list(ship.shipphoto_set.values_list('url', flat=True))
    delete_if_unused(ship, owned=[ShipCurrency, ShipAmenity, ShipPhoto])
    transaction.on_commit(lambda: [delete_file(url) for url in photo_urls])


# -- Photos

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


# -- Helpers

def _set_currencies(ship, currencies):
    ShipCurrency.objects.bulk_create([ShipCurrency(ship=ship, currency=currency) for currency in currencies])


def _amenities_to_attach(amenity_ids, new_names, *, already_attached=frozenset()) -> list[Amenity]:
    """
    The amenities a ship should have: the chosen ones plus the named ones. A name matches an existing amenity
    regardless of case, and names not yet in the master list are added to it.

    Only active amenities can be added. Amenities the ship already has may stay even if they've been deactivated
    since, so editing a ship never forces staff to remove them.
    """
    usable = Amenity.objects.filter(Q(is_active=True) | Q(id__in=already_attached))
    chosen = list(usable.filter(id__in=amenity_ids))
    unusable = set(amenity_ids) - {amenity.id for amenity in chosen}

    errors = [{'field': 'amenity_ids', 'message': f'No active amenity with id {amenity_id}'}
              for amenity_id in sorted(unusable, key=str)]
    named = []
    for name in new_names:
        amenity = Amenity.objects.filter(name__iexact=name).first() or Amenity.objects.create(name=name)
        if amenity.is_active or amenity.id in already_attached:
            named.append(amenity)
        else:
            errors.append({'field': 'new_amenities', 'message': f'"{amenity.name}" exists but is inactive'})

    if errors:
        raise ValidationFailedError(detail='Some amenities can\'t be added.', errors=errors)
    return chosen + named
