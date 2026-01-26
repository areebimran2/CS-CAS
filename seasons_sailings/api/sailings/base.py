from ninja import Router

router = Router(tags=['F2. Sailing'])

@router.get('')
def list_sailings(request):
    """
    Returns a list of sailings.
    """