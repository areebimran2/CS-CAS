from django.shortcuts import get_object_or_404
from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from routes.models import Route
from routes.schemas import RouteOut, RouteIn

router = Router(tags=['E1. Routes + Legs'])

@router.get('', response=NinjaPaginationResponseSchema[RouteOut])
@paginate()
def list_routes(request):
    """
    Returns a list of routes that define "the ports a ship visits in order".
    """
    return Route.objects.all()

@router.post('', response=RouteOut)
def create_route(request, payload: RouteIn):
    """
    Creates a new route.
    """
    route = Route.objects.create(**payload.dict(exclude_unset=True))
    return route

@router.get('/{route_id}', response=RouteOut)
def get_route(request, route_id):
    """
    Returns a route by ID.
    """
    route = get_object_or_404(Route, id=route_id)
    return route

@router.put('/{route_id}', response=RouteOut)
def update_route(request, payload: RouteIn, route_id):
    """
    Updates a routes base fields.
    """
    route = get_object_or_404(Route, id=route_id)

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(route, attr, value)

    route.save()
    return route