from ninja import Router

router = Router(tags=['C4. FX'])

@router.get('/fx/manual-rates')
def list_manual_rates(request):
    """
    Returns a list of all stored FX pairs and their rates.
    """