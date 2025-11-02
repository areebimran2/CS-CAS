from ninja import Router
from ninja_jwt.authentication import JWTAuth

from .routes.session import router as session_router
from .routes.tfa import router as tfa_router
from .routes.profile import router as profile_router

router = Router(tags=['Auth'])
router.add_router('', session_router)
router.add_router('/2fa', tfa_router)
router.add_router('/me', profile_router, auth=JWTAuth())

