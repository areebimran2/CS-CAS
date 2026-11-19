from ninja import Router

from .permissions import router as permissions_router
from .roles import router as roles_router
from .users import router as users_router

admin_router = Router()
admin_router.add_router('users', users_router)
admin_router.add_router('roles', roles_router)
admin_router.add_router('permissions', permissions_router)

__all__ = ['admin_router']
