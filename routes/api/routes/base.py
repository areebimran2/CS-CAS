from ninja import Router

router = Router(tags=['E1. Routes + Legs'])

@router.get('')
def list_routes(request):
    """
    Returns a list of routes that define "the ports a ship visits in order".
    """