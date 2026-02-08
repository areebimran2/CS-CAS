from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from seasons_sailings.schemas import *

router = Router(tags=['F1. Season'])

@router.get('', response=NinjaPaginationResponseSchema[SeasonOut])
@paginate()
def list_seasons(request):
    """
    Returns a list of seasons.
    """

@router.post('', response=SeasonOut)
def create_season(request, payload: SeasonIn):
    """
    Creates a new season.

    Note: ships are assigned using a dedicated endpoint
    """

@router.get('/{season_id}', response=SeasonOut)
def get_season(request, season_id):
    """
    Returns a season by ID.
    """

@router.put('/{season_id}', response=SeasonOut)
def update_season(request, payload: SeasonIn, season_id):
    """
    Updates a seasons fields.
    """

@router.put('/{season_id}/ships', response=SeasonOut)
def assign_ships(request, payload: AssignShips, season_id):
    """
    Replaces the season <-> ship assignments.
    """

@router.post('/validate-overlap', response=ValidateOverlapSeasonsOut)
def validate_overlap(request, payload: ValidateOverlapSeasonsIn):
    """
    A preliminary overlap check used by the UI before saving changes. It checks whether the proposed date range overlaps
    with an existing season.
    """