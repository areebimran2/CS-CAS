from ninja import Router

router = Router(tags=['D1. Ships'])

@router.get('')
def list_ships(request):
    """
    Returns a list of active ships.
    """