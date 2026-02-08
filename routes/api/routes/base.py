from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from routes.schemas import *

router = Router(tags=['E1. Routes + Legs'])

@router.get('', response=NinjaPaginationResponseSchema[RouteOut])
@paginate()
def list_routes(request):
    """
    Returns a list of routes that define "the ports a ship visits in order".
    """

@router.post('', response=RouteOut)
def create_route(request, payload: RouteIn):
    """
    Creates a new route.
    """

@router.get('/{route_id}', response=RouteOut)
def get_route(request, route_id):
    """
    Returns a route by ID.
    """

@router.put('/{route_id}', response=RouteOut)
def update_route(request, payload: RouteIn, route_id):
    """
    Updates a routes base fields.
    """