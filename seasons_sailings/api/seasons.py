import uuid

from ninja import Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from seasons_sailings.schemas import (
    SeasonFilter,
    SeasonIn,
    SeasonOut,
    SeasonShipsIn,
    ValidateOverlapSeasonsIn,
    ValidateOverlapSeasonsOut,
)

router = Router(tags=['F1. Seasons'])


@router.get('', response=NinjaPaginationResponseSchema[SeasonOut])
@requires('seasons.view')
@paginate()
def list_seasons(request, filters: Query[SeasonFilter]):
    """
    Returns the seasons by start date. By default only current seasons; `?archived=true` lists archived ones and
    `?archived=all` both. `?search=` matches the name.
    """


@router.post('', response=SeasonOut)
@requires('seasons.create')
def create_season(request, payload: SeasonIn):
    """
    Creates a season. Seasons may not overlap (409 `SEASON_OVERLAP`). Assign its ships with `PUT .../ships`.
    """


@router.post('/validate-overlap', response=ValidateOverlapSeasonsOut)
@requires('seasons.view')
def validate_season_overlap(request, payload: ValidateOverlapSeasonsIn):
    """
    Checks whether a proposed date range overlaps an existing season, so the UI can warn before saving.
    """


@router.get('/{season_id}', response=SeasonOut)
@requires('seasons.view')
def get_season(request, season_id: uuid.UUID):
    """
    Returns a season with the ids of its ships.
    """


@router.put('/{season_id}', response=SeasonOut)
@requires('seasons.edit')
def replace_season(request, payload: SeasonIn, season_id: uuid.UUID):
    """
    Replaces a season's name, dates and default margins.
    """


@router.put('/{season_id}/ships', response=SeasonOut)
@requires('seasons.edit')
def replace_season_ships(request, payload: SeasonShipsIn, season_id: uuid.UUID):
    """
    Replaces the ships that operate in the season.
    """


@router.post('/{season_id}/archive', response=SeasonOut)
@requires('seasons.edit')
def archive_season(request, season_id: uuid.UUID):
    """
    Archives a season, which hides it from the default season list. Its sailings and pricing are kept.
    """


@router.post('/{season_id}/unarchive', response=SeasonOut)
@requires('seasons.edit')
def unarchive_season(request, season_id: uuid.UUID):
    """
    Restores an archived season.
    """


@router.delete('/{season_id}', response={204: None})
@requires('seasons.delete')
def delete_season(request, season_id: uuid.UUID):
    """
    Deletes a season that nothing refers to: no sailings or pricing. Otherwise responds 409 `IN_USE`; archive it
    instead.
    """
