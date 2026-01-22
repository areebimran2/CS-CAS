from ninja import Router

from ninja_jwt.authentication import JWTAuth

from .auth.base import router as auth_base_router
from .auth.tfa import router as auth_tfa_router

from .me.base import router as me_base_router

auth_router = Router()
auth_router.add_router('', auth_base_router)
auth_router.add_router('/2fa', auth_tfa_router)

me_router = Router()
me_router.add_router('', me_base_router, auth=JWTAuth())
