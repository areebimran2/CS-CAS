from ninja import NinjaAPI

from common.exceptions import APIErrorManager
from myauth.api import router as myauth_router

api = NinjaAPI()

APIErrorManager(api)

api.add_router('auth/', myauth_router)