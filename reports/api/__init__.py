from ninja import Router

from .reports import router as report_router
from .schedules import router as schedules_router

reports_router = Router()
reports_router.add_router('', report_router)
reports_router.add_router('schedules/', schedules_router)

__all__ = ['reports_router']
