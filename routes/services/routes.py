from django.db import transaction

from common.services import update_instance
from routes.models import Route, RouteLeg


@transaction.atomic
def create_route(*, legs: list[dict], **fields) -> Route:
    route = Route.objects.create(**fields)
    _create_legs(route, legs)
    return route


@transaction.atomic
def update_route(route: Route, changes: dict) -> Route:
    """Apply a partial update. A leg list, if given, replaces all of the route's legs."""
    changes = dict(changes)
    if (legs := changes.pop('legs', None)) is not None:
        route.routeleg_set.all().delete()
        _create_legs(route, legs)
    return update_instance(route, changes)


def _create_legs(route, legs):
    RouteLeg.objects.bulk_create([RouteLeg(route=route, **leg) for leg in legs])
