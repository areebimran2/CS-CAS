from ninja import Router

router = Router(tags=['D3. Cabins'])

@router.get('')
def list_cabins(request):
    """
    Returns a list of cabins that belong to the specified ship.
    """