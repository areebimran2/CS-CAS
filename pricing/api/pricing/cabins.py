from ninja import Router

from common.access import requires
from pricing.schemas import CabinOverrideIn

router = Router(tags=['G2. Sailing-scoped Cabin Pricing'])

@router.put('/{cabin_id}')
@requires('pricing.edit')
def cabin_override(request, payload: CabinOverrideIn, sailing_id, cabin_id):
    """
    Per-cabin override (and optionally its custom costs) for a selected cabin in a specific sailing.
    """