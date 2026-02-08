from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from ships_cabins.schemas import *

router = Router(tags=['D1. Ships'])

@router.get('', response=NinjaPaginationResponseSchema[ShipOut])
@paginate()
def list_ships(request):
    """
    Returns a list of active ships.
    """

@router.post('', response=ShipOut)
def create_ship(request, payload: ShipIn):
    """
    Creates a new ship.
    """

@router.get('/{ship_id}', response=ShipOut)
def get_ship(request, ship_id):
    """
    Returns a ship by ID.
    """

@router.put('/{ship_id}', response=ShipOut)
def update_ship(request, payload: ShipUpdateIn, ship_id):
    """
    Update a ships name, operator, contact person or address.
    """

@router.put('/{ship_id}/currencies', response=ShipOut)
def set_ship_currencies(request, payload: ShipCurrenciesIn, ship_id):
    """
    Replace a ships currencies list.
    """

@router.put('/{ship_id}/amenities', response=ShipOut)
def set_ship_amenities(request, payload: ShipAmenitiesIn, ship_id):
    """
    Replace a ships amenities list.
    """

@router.put('/{ship_id}/photos', response=ShipOut)
def add_ship_photo(request, payload: ShipPhotoIn, ship_id):
    """
    Add a photo to the ship gallery.
    """