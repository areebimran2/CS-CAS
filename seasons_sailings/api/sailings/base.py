from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from seasons_sailings.schemas import *
from ships_cabins.schemas import CabinOut

router = Router(tags=['F2. Sailing'])

@router.get('', response=NinjaPaginationResponseSchema[SailingOut])
def list_sailings(request):
    """
    Returns a list of sailings.
    """

@router.post('', response=SailingOut)
def create_sailing(request, payload: SailingIn):
    """
    Creates a sailing for a ship in a season.
    """

@router.get('/{sailing_id}', response=SailingOut)
def get_sailing(request, sailing_id):
    """
    Returns a sailing by ID.
    """

@router.put('/{sailing_id}', response=SailingOut)
def update_sailing(request, payload: SailingIn, sailing_id):
    """
    Updates a sailings fields.
    """

@router.post('/validate-overlap', response=ValidateOverlapSailingsOut)
def validate_overlap(request, payload: ValidateOverlapSailingsIn):
    """
    A preliminary overlap check used by the UI before saving changes. It checks the per-ship no-overlap rule for a
    proposed sailing window.

    Note: an optional `season` can be provided to check for the "end after season end" warning.
    """

@router.get('/{sailing_id}/summary', response=SummaryOut)
def get_summary_sailing(request, sailing_id):
    """
    Returns a compact "header" summary of the sailing potentially used by selling/pricing list screens.
    """

@router.get('/{sailing_id}/cabins', response=NinjaPaginationResponseSchema[CabinOut])
@paginate()
def get_sailing_cabins(request, sailing_id):
    """
    Returns a list of cabins relevant to the sailing.
    """

@router.get('/{sailing_id}/availability', response=NinjaPaginationResponseSchema[CabinAvailabilityOut])
def get_sailing_availability(request, sailing_id):
    """
    Returns the per-cabin availability status for the sailing.
    """