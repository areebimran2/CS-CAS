from ninja import Router

from .routes.base import router as routes_base_router
from .routes.legs import router as routes_legs_router

routes_router = Router()
routes_router.add_router('', routes_base_router)
routes_router.add_router('{route_id}/legs/', routes_legs_router)