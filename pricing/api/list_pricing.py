from ninja import Query, Router

from common.access import requires
from pricing.schemas import ListPricingFilter, ListPricingOut

router = Router(tags=['H1. List Pricing'])


@router.get('', response=ListPricingOut)
@requires('pricing.view')
def get_list_pricing(request, filters: Query[ListPricingFilter]):
    """
    Totals of cost of sale and B2B/B2C sales, grouped season → ship → sailing, with overall totals. Filter by season,
    ships, departure range, nights, route, category, deck, pricing status and search; choose the FX mode and
    occupancy. Drill down with `GET /api/pricing/lines` for a sailing's cabins and
    `GET /api/pricing/sailings/{sailing_id}/cabins/{cabin_id}` for one cabin. Export with `/api/exports/pricing`.
    """
