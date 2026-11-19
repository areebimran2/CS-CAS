from ninja import Router

from common.access import requires
from selling.schemas import UcRefIn, ZohoDetailsOut

router = Router(tags=['I1. UC Ref Lookup'])


@router.post('/fetch-by-uc-ref', response=ZohoDetailsOut)
@requires('selling.view')
def fetch_by_uc_ref(request, payload: UcRefIn):
    """
    Looks up a UC Ref in Zoho and returns the deal name, channel, agency, agent and contacts, to prefill a hold or
    booking.
    """
