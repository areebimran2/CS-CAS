from ninja import Query, Router

from common.access import requires
from pricing.schemas import PricingBulkIn, PricingBulkOut, PricingGraphOut, PricingLinesOut, PricingScope

router = Router(tags=['G1. Pricing'])


@router.get('/graph', response=PricingGraphOut)
@requires('pricing.view')
def get_pricing_graph(request, scope: Query[PricingScope]):
    """
    The interactive graph view: every cabin on each selected sailing with its pricing status (priced, unpriced,
    review, overridden, archived) and coverage counts.
    """


@router.get('/lines', response=PricingLinesOut)
@requires('pricing.view')
def get_pricing_lines(request, scope: Query[PricingScope]):
    """
    The list view: each cabin on each selected sailing with its full price breakdown, plus cost of sale and B2B/B2C
    sales totals for 2-pax or single occupancy.
    """


@router.post('/bulk', response=PricingBulkOut)
@requires('pricing.edit')
def set_bulk_pricing(request, payload: PricingBulkIn):
    """
    Sets the base cost per passenger, currency, single multiplier and custom costs for the targeted cabins (by
    category, deck or selection) on each selected sailing. Per-cabin overrides are kept.
    """
