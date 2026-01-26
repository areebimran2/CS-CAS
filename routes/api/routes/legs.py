from ninja import Router

router = Router(tags=['E1. Routes + Legs'])

@router.get('')
def list_route_legs(request):
    """
    Returns the ordered list of route legs (actual ports/stops) for the specified route.
    """