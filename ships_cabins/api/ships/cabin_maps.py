from ninja import Router

router = Router(tags=['D2. Cabin Maps'])

@router.get('')
def list_cabin_maps(request):
    """
    Returns a list of the map versions that belong to the specified ship.
    """