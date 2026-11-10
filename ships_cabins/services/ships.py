from catalogs.models import Amenity
from ships_cabins.models import ShipCurrency, ShipAmenity, Ship


def create_ship_joins(ship, currencies, amenities, new_amenities):
    """
    Creates the 'currencies' and 'new_amenities' ship join sets.
    """
    # Create ShipCurrency join rows for the selected currencies
    ship_currencies = [ShipCurrency(ship=ship, currency=currency) for currency in currencies]
    ShipCurrency.objects.bulk_create(ship_currencies)

    # Create any brand-new amenities in the master list
    ship_new_amenities = [Amenity(name=name) for name in new_amenities]
    Amenity.objects.bulk_create(
        ship_new_amenities,
        ignore_conflicts=True,
        unique_fields=['name']
    )

    # Collect all amenity IDs: the explicitly-selected ones + the new ones
    new_amenity_ids = Amenity.objects.filter(
        name__in=new_amenities
    ).values_list('id', flat=True)

    all_amenity_ids = set(amenities) | set(new_amenity_ids)

    # Create ShipAmenity join rows (same pattern as ShipCurrency)
    ship_amenities = [ShipAmenity(ship=ship, amenity_id=aid) for aid in all_amenity_ids]
    ShipAmenity.objects.bulk_create(
        ship_amenities,
        ignore_conflicts=True
    )