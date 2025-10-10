from ninja import NinjaAPI

from common.exceptions import APIExceptionManager
from myauth.api import router as myauth_router

api = NinjaAPI()

APIExceptionManager(api)

api.add_router('auth/', myauth_router)