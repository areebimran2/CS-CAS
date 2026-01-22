from ninja import Router

from .discounts.base import router as discounts_base_router

discounts_router = Router()
discounts_router.add_router('', discounts_base_router)