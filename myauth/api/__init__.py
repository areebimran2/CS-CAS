from ninja import Router

from .auth import router as login_router
from .me import router as me_router
from .tfa import router as tfa_router

auth_router = Router()
auth_router.add_router('', login_router)
auth_router.add_router('/2fa', tfa_router)

__all__ = ['auth_router', 'me_router']
