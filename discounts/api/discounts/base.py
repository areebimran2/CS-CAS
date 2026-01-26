from ninja import Router

router = Router(tags=['J1. Discounts'])

@router.get('')
def list_discounts(request):
    """
    Returns a list of discount "summaries".
    """