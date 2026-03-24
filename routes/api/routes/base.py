from django.shortcuts import get_object_or_404
from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from routes.models import Route, RouteLeg
from routes.schemas import RouteOut, RouteIn, RouteOutWithLegs

router = Router(tags=['E1. Route'])

@router.get('', response=NinjaPaginationResponseSchema[RouteOut])
@paginate()
def list_routes(request):
    """
    Returns a list of routes that define "the ports a ship visits in order".
    """
    return Route.objects.all()

@router.post('', response=RouteOutWithLegs)
def create_route(request, payload: RouteIn):
    """
    Creates a new route.
    """
    payload_dict = payload.dict(exclude=['legs'], exclude_unset=True)
    route = Route.objects.create(**payload_dict)

    legs = [RouteLeg(seq=leg.seq,
                     place_id=leg.place_id,
                     lat=leg.lat,
                     lng=leg.lng,
                     tz=leg.tz,
                     route=route)
             for leg in payload.legs]

    RouteLeg.objects.bulk_create(
        legs,
        unique_fields=['seq', 'route']
    )

    return route

@router.get('/{route_id}', response=RouteOutWithLegs)
def get_route(request, route_id):
    """
    Returns a route by ID.
    """
    route = get_object_or_404(Route, id=route_id)
    return route

@router.put('/{route_id}', response=RouteOutWithLegs)
def update_route(request, payload: PatchDict[RouteIn], route_id):
    """
    Updates a routes base fields.
    """
    route = get_object_or_404(Route, id=route_id)

    data = dict(payload)
    legs = data.pop('legs', [])

    for attr, value in data.items():
        setattr(route, attr, value)

    legs = [RouteLeg(seq=leg['seq'],
                     place_id=leg['place_id'],
                     lat=leg['lat'],
                     lng=leg['lng'],
                     tz=leg['tz'],
                     route=route)
            for leg in legs]

    RouteLeg.objects.bulk_create(
        legs,
        update_conflicts=True,
        update_fields=['seq', 'place_id', 'lat', 'lng', 'tz'],
        unique_fields=['seq', 'route']
    )

    route.save()
    return route