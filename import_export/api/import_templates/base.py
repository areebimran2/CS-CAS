from ninja import Router

from common.access import requires

router = Router(tags=['K1. Templates'])


@router.get('')
@requires('data.import')
def placeholder(request):
    """

    """