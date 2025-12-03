from ninja import Router
from ninja_jwt.authentication import JWTAuth

from .routes.users import router as users_router
from .routes.roles import router as roles_router


router = Router(tags=['Admin'])
router.add_router('/users', users_router)
router.add_router('/roles', roles_router)

