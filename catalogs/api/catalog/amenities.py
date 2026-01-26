from ninja import Router

router = Router(tags=['C1. Amenities'])

@router.get('')
def list_amenities(request):
    """
    Returns a list of available amenities in the system.
    """