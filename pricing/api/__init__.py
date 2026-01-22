from ninja import Router

from .pricing.base import router as pricing_base_router
from .pricing.cabins import router as pricing_cabins_router
from .pricing.list import router as pricing_list_router

pricing_router = Router()
pricing_router.add_router('', pricing_base_router)
pricing_router.add_router('{sailing_id}/cabins/', pricing_cabins_router)
pricing_router.add_router('list/', pricing_list_router)