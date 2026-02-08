from ninja import Router
from ninja_extra import paginate

from pricing.schemas import PricingGraphOut, PricingListOut, CabinOverrideIn

router = Router(tags=['G1. Scope, View, Bulk, Margins & FX'])

@router.get('/graph', response=PricingGraphOut)
def get_pricing_graph(request, season_id, ship_id, sailing_ids, fx_mode, occupancy):
    """
    Pricing Interactive Graph view for a selected scope.

    This returns a grid/coverage-oriented pricing breakdown.
    """

@router.get('/lines', response=PricingListOut)
@paginate()
def get_pricing_list(request, season_id, ship_id, sailing_ids, fx_mode, occupancy):
    """
    Pricing List view for a selected scope.

    This returns paginated cabin line items.
    """

@router.post('/bulk')
def pricing_bulk(request):
    """
    Bulk set pricing inputs (base/currency/single multiplier/custom costs) for a target set: Category / Deck /
    selected Cabins, and apply across the selected Sailing
    """