from ninja import Router

from common.access import requires

router = Router(tags=['K3. Export'])

@router.get('')
@requires('data.export')
def placeholder(request):
    """

    """
