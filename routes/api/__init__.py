from ninja import Router

from .routes.base import router as routes_base_router
from .places.base import router as places_base_router

routes_router = Router()
routes_router.add_router('', routes_base_router)

places_router = Router()
places_router.add_router('', places_base_router)