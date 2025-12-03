from ninja import NinjaAPI

from common.exceptions import APIErrorManager
from myauth.api import router as myauth_router
from myadmin.api import router as myadmin_router

api = NinjaAPI()

APIErrorManager(api)

api.add_router('auth/', myauth_router)
api.add_router('admin/', myadmin_router)