import uuid

from ninja import Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from seasons_sailings.schemas import (
    CabinAvailabilityOut,
    SailingBulkIn,
    SailingFilter,
    SailingIn,
    SailingOut,
    SummaryOut,
    ValidateOverlapSailingsIn,
    ValidateOverlapSailingsOut,
)

router = Router(tags=['F2. Sailings'])


@router.get('', response=NinjaPaginationResponseSchema[SailingOut])
@requires('sailings.view')
@paginate()
def list_sailings(request, filters: Query[SailingFilter]):
    """
    Returns sailings by departure date. Filter by `?season_id=`, `?ship_id=` (repeatable), `?route_id=`, `?nights=`,
    and a departure range with `?departure_from=` and `?departure_to=`.
    """


@router.post('', response=SailingOut)
@requires('sailings.create')
def create_sailing(request, payload: SailingIn):
    """
    Creates a sailing: a departure date and number of nights for a ship in a season. A ship can't have overlapping
    sailings (409 `SAILING_OVERLAP`); ending after the season ends is allowed.
    """


@router.post('/bulk', response=list[SailingOut])
@requires('sailings.create')
def create_sailings(request, payload: SailingBulkIn):
    """
    Creates up to 500 sailings at once, or none: if any is invalid or overlaps, nothing is saved and every problem is
    listed with its row, e.g. `sailings[3].departure_date`.
    """


@router.post('/validate-overlap', response=ValidateOverlapSailingsOut)
@requires('sailings.view')
def validate_sailing_overlap(request, payload: ValidateOverlapSailingsIn):
    """
    Checks a proposed sailing against the ship's other sailings, and whether it ends after its season, so the UI can
    warn before saving.
    """


@router.get('/{sailing_id}', response=SailingOut)
@requires('sailings.view')
def get_sailing(request, sailing_id: uuid.UUID):
    """
    Returns a sailing.
    """


@router.put('/{sailing_id}', response=SailingOut)
@requires('sailings.edit')
def replace_sailing(request, payload: SailingIn, sailing_id: uuid.UUID):
    """
    Replaces a sailing's season, ship, route, departure date and nights.
    """


@router.delete('/{sailing_id}', response={204: None})
@requires('sailings.delete')
def delete_sailing(request, sailing_id: uuid.UUID):
    """
    Deletes a sailing that nothing refers to: no pricing, discounts, holds or bookings. Otherwise responds 409
    `IN_USE`.
    """


@router.get('/{sailing_id}/summary', response=SummaryOut)
@requires('sailings.view')
def get_sailing_summary(request, sailing_id: uuid.UUID):
    """
    Returns a compact header for selling and pricing screens: the sailing with its ship, season and route.
    """


@router.get('/{sailing_id}/availability', response=list[CabinAvailabilityOut])
@requires('sailings.view')
def get_sailing_availability(request, sailing_id: uuid.UUID):
    """
    Returns each of the ship's current cabins with its status on this sailing (available, reserved or booked) and the
    hold or booking behind it. This colours the interactive cabin map.
    """
