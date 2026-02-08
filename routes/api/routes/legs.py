from ninja import Router, Path
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from routes.schemas import *

router = Router(tags=['E1. Routes + Legs'])


@router.get('', response=NinjaPaginationResponseSchema[RouteLegOut])
@paginate()
def list_route_legs(request, route_id: str = Path(...)):
    """
    Returns the ordered list of route legs (actual ports/stops) for the specified route.
    """

@router.post('', response=RouteLegOut)
def create_route_leg(request, payload: RouteLegIn, route_id: str = Path(...)):
    """
    Adds a new leg to the specified route.

    Note: omitting `seq` will append the leg to the end of the sequence.
    """

@router.put('/{leg_id}', response=RouteLegOut)
def update_route_leg(request, payload: RouteLegUpdateIn, leg_id, route_id: str = Path(...)):
    """
    Update the port (place fields) of a single leg of the specified route.

    Note: sequence changes are to be done through `/reorder`
    """

@router.post('/reorder', response=List[RouteLegOut])
def reorder_route_legs(request, payload: RouteLegReorderIn, route_id: str = Path(...)):
    """
    Reorders the legs for the specified route in bulk.

    Note: The full set of route legs for the specified route is required to guarantee correct ordering.
    """