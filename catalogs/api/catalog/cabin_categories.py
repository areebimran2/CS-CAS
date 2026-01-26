from ninja import Router

router = Router(tags=['C2. Cabin Categories'])

@router.get('')
def list_cabin_categories(request):
    """
    Returns a list of all valid cabin categories.
    """