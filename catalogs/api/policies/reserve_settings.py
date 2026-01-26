from ninja import Router

router = Router(tags=['C5. Reserve Settings'])

@router.get('')
def get_reserve_settings(request):
    """
    Returns the active global reservation ruleset configuration.
    """