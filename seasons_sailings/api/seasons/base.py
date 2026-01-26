from ninja import Router

router = Router(tags=['F1. Season'])

@router.get('')
def list_seasons(request):
    """
    Returns a list of seasons.
    """