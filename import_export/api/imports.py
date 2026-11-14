from ninja import Router

from common.access import requires

router = Router(tags=['K2. Import'])


@router.get('')
@requires('data.import')
def placeholder(request):
    """

    """