from ninja import Router, Path, PatchDict

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from ships_cabins.schemas import CabinOut, CabinIn

router = Router(tags=['D3. Cabins'])

@router.get('', response=NinjaPaginationResponseSchema[CabinOut])
@requires('ships.view')
@paginate()
def list_cabins(request, ship_id: str = Path(...)):
    """
    Returns a list of cabins that belong to the specified ship.
    """

@router.post('', response=CabinOut)
@requires('ships.create')
def create_cabin(request, payload: CabinIn, ship_id: str = Path(...)):
    """
    Creates a new cabin.
    """

@router.get('/{cabin_id}', response=CabinOut)
@requires('ships.view')
def get_cabin(request, cabin_id, ship_id: str = Path(...)):
    """
    Returns a cabin by id.
    """

@router.put('/{cabin_id}', response=CabinOut)
@requires('ships.edit')
def update_cabin(request, payload: PatchDict[CabinIn], cabin_id, ship_id: str = Path(...)):
    """
    Updates a cabin.
    """