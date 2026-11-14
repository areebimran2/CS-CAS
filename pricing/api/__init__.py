from ninja import Router

from .cabins import router as cabins_router
from .list_pricing import router as list_pricing_router
from .pricing import router as scope_router

pricing_router = Router()
pricing_router.add_router('', scope_router)
pricing_router.add_router('{sailing_id}/cabins/', cabins_router)
pricing_router.add_router('list/', list_pricing_router)

__all__ = ['pricing_router']
