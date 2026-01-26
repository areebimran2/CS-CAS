from ninja import Router

router = Router(tags=['C3. Custom Costs'])

@router.get('')
def list_custom_costs(request):
    """
    Returns a list of all configurable cost types used for pricing.
    """