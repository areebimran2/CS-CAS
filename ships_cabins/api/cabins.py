import uuid
from typing import List

from django.shortcuts import get_object_or_404
from ninja import PatchDict, Path, Query, Router, Status
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from ships_cabins.models import Cabin, Ship
from ships_cabins.schemas import CabinBulkIn, CabinFilter, CabinIn, CabinOut, DeckOut
from ships_cabins.services import cabins as service

router = Router(tags=['D3. Cabins'])



@router.get('', response=NinjaPaginationResponseSchema[CabinOut])
@requires('ships.view')
@paginate()
def list_cabins(request, filters: Query[CabinFilter], ship_id: uuid.UUID = Path(...)):
    """
    Returns the ship's cabins in number order (3, 4, ..., 10). By default only current cabins; `?archived=true` lists
    archived ones and `?archived=all` both. Filter with `?deck=`, `?category_id=` (repeatable) and `?search=` (number
    or name).
    """
    ship = get_object_or_404(Ship, id=ship_id)
    return filters.filter(ship.cabin_set.select_related('category'))


@router.post('', response=CabinOut)
@requires('ships.create')
def create_cabin(request, payload: CabinIn, ship_id: uuid.UUID = Path(...)):
    """
    Creates a cabin. Its number must be unique on the ship, ignoring case.
    """
    ship = get_object_or_404(Ship, id=ship_id)
    return service.create_cabin(ship, **payload.dict())


@router.post('/bulk', response=List[CabinOut])
@requires('ships.create')
def create_cabins(request, payload: CabinBulkIn, ship_id: uuid.UUID = Path(...)):
    """
    Creates up to 500 cabins at once, or none: if any row is invalid, nothing is saved and every problem is listed with
    its row, e.g. `cabins[3].number`.
    """
    ship = get_object_or_404(Ship, id=ship_id)
    return service.create_cabins(ship, payload.dict()['cabins'])


@router.get('/decks', response=List[DeckOut])
@requires('ships.view')
def list_decks(request, ship_id: uuid.UUID = Path(...)):
    """
    Returns each deck that has current cabins, with how many, so clients can offer the decks already in use.
    """
    ship = get_object_or_404(Ship, id=ship_id)
    return service.decks(ship)


@router.get('/{cabin_id}', response=CabinOut)
@requires('ships.view')
def get_cabin(request, cabin_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Returns a cabin.
    """
    return get_object_or_404(Cabin.objects.select_related('category'), ship_id=ship_id, id=cabin_id)


@router.put('/{cabin_id}', response=CabinOut)
@requires('ships.edit')
def update_cabin(request, payload: PatchDict[CabinIn], cabin_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Updates a cabin. Only the fields sent are changed. A cabin can't move to another ship.
    """
    cabin = get_object_or_404(Cabin.objects.select_related('category'), ship_id=ship_id, id=cabin_id)
    return service.update_cabin(cabin, payload)


@router.post('/{cabin_id}/archive', response=CabinOut)
@requires('ships.edit')
def archive_cabin(request, cabin_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Archives a cabin, which hides it from the default cabin list. Its history is kept.
    """
    cabin = get_object_or_404(Cabin.objects.select_related('category'), ship_id=ship_id, id=cabin_id)
    return service.set_cabin_archived(cabin, True)


@router.post('/{cabin_id}/unarchive', response=CabinOut)
@requires('ships.edit')
def unarchive_cabin(request, cabin_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Restores an archived cabin.
    """
    cabin = get_object_or_404(Cabin.objects.select_related('category'), ship_id=ship_id, id=cabin_id)
    return service.set_cabin_archived(cabin, False)


@router.delete('/{cabin_id}', response={204: None})
@requires('ships.delete')
def delete_cabin(request, cabin_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Deletes a cabin that nothing refers to (cabin maps, pricing, discounts, holds or bookings). Otherwise responds
    409 `IN_USE`; archive the cabin instead.
    """
    cabin = get_object_or_404(Cabin.objects.select_related('category'), ship_id=ship_id, id=cabin_id)
    service.delete_cabin(cabin)
    return Status(204, None)
