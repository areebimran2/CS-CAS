from ninja import Router

from .cabin_maps import router as cabin_maps_router
from .cabins import router as cabins_router
from .ships import router as ship_router

ships_router = Router()
ships_router.add_router('', ship_router)
ships_router.add_router('{ship_id}/cabin-maps/', cabin_maps_router)
ships_router.add_router('{ship_id}/cabins/', cabins_router)

__all__ = ['ships_router']
