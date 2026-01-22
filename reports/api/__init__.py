from ninja import Router

from .reports.base import router as reports_base_router
from .reports.schedules import router as reports_schedules_router

reports_router = Router()
reports_router.add_router('', reports_base_router)
reports_router.add_router('schedules/', reports_schedules_router)