from ninja import Router

from .amenities import router as amenities_router
from .cabin_categories import router as cabin_categories_router
from .cancellation_policies import router as cancellation_policies_router
from .custom_costs import router as custom_costs_router
from .fx import router as fx_router
from .reserve_settings import router as reserve_settings_router

catalogs_router = Router()
catalogs_router.add_router('amenities', amenities_router)
catalogs_router.add_router('cabin-categories', cabin_categories_router)
catalogs_router.add_router('custom-costs', custom_costs_router)

policies_router = Router()
policies_router.add_router('reserve-settings', reserve_settings_router)
policies_router.add_router('cancellation-policies', cancellation_policies_router)

__all__ = ['catalogs_router', 'fx_router', 'policies_router']
