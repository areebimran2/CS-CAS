from .list_pricing import router as list_pricing_router
from .pricing import router as pricing_router
from .sailings import router as sailing_overrides_router
from .ship_custom_costs import router as ship_custom_costs_router

# The other pricing resources are mounted on the main pricing router: /pricing/list, /pricing/sailings/{sailing_id}.
# (Mounting a parent at '' under another router would give its root path a trailing slash.)
pricing_router.add_router('list', list_pricing_router)
pricing_router.add_router('sailings/{sailing_id}', sailing_overrides_router)
pricing_router.add_router('ships/{ship_id}/custom-costs', ship_custom_costs_router)

__all__ = ['pricing_router']
