from ninja import NinjaAPI

from myauth.api import router as myauth_router

api = NinjaAPI()

api.add_router('auth/', myauth_router)