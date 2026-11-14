from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from routes.models import Route
from routes.schemas import RouteIn, RouteOut, RouteOutWithLegs
from routes.services import routes as service

router = Router(tags=['E1. Route'])


@router.get('', response=NinjaPaginationResponseSchema[RouteOut])
@requires('routes.view')
@paginate()
def list_routes(request):
    """
    Returns a list of routes that define "the ports a ship visits in order".
    """
    return Route.objects.all()


@router.post('', response=RouteOutWithLegs)
@requires('routes.create')
def create_route(request, payload: RouteIn):
    """
    Creates a new route.
    """
    return service.create_route(**payload.dict(exclude_unset=True))


@router.get('/{route_id}', response=RouteOutWithLegs)
@requires('routes.view')
def get_route(request, route_id):
    """
    Returns a route by ID.
    """
    return get_object_or_404(Route, id=route_id)


@router.put('/{route_id}', response=RouteOutWithLegs)
@requires('routes.edit')
def update_route(request, payload: PatchDict[RouteIn], route_id):
    """
    Updates a route. Only the fields sent are changed; sending `legs` replaces all of the route's legs.
    """
    return service.update_route(get_object_or_404(Route, id=route_id), payload)
