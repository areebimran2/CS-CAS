from ninja import Router

from .seasons.base import router as seasons_base_router
from .sailings.base import router as sailings_base_router

seasons_router = Router()
seasons_router.add_router('', seasons_base_router)

sailings_router = Router()
sailings_router.add_router('', sailings_base_router)