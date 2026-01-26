from ninja import Router

router = Router(tags=['C6. Cancellation Policies'])

@router.get('')
def list_cancellation_policies(request):
    """
    Returns a list of valid cabin cancellation policies available for selection.
    """