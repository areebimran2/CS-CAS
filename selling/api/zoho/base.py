from ninja import Router

from selling.schemas import ZohoDetailsOut

router = Router(tags=['I1. UC Ref Lookup'])

@router.post('/fetch-by-uc-ref', response=ZohoDetailsOut)
def zoho_fetch(request):
    """
    Return zoho deal details given a UC Ref.
    """