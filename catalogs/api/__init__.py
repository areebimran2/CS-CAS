from ninja import Router

from .catalog.amenities import router as catalogs_amenities_router
from .catalog.cabin_categories import router as catalogs_cabin_categories_router
from .catalog.custom_costs import router as catalogs_custom_costs_router

from .fx.base import router as fx_base_router

from .policies.reserve_settings import router as policy_reserve_settings_router
from .policies.cancellation_policies import router as policy_cancellation_router

catalogs_router = Router()
catalogs_router.add_router('amenities/', catalogs_amenities_router)
catalogs_router.add_router('cabin-categories/', catalogs_cabin_categories_router)
catalogs_router.add_router('custom-costs/', catalogs_custom_costs_router)

fx_router = Router()
fx_router.add_router('', fx_base_router)

policies_router = Router()
policies_router.add_router('reserve-settings/', policy_reserve_settings_router)
policies_router.add_router('cancellation-policies/', policy_cancellation_router)