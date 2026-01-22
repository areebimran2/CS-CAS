from ninja import Router

from .ships.base import router as ships_base_router
from .ships.cabin_maps import router as ships_cabin_maps_router
from .ships.cabins import router as ships_cabins_router

ships_router = Router()
ships_router.add_router('', ships_base_router)
ships_router.add_router('{ship_id}/cabin-maps/', ships_cabin_maps_router)
ships_router.add_router('{ship_id}/cabins/', ships_cabins_router)