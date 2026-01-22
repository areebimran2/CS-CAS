from ninja import Router

from .admin.users import router as admin_users_router
from .admin.roles import router as admin_roles_router
from .admin.permissions import router as admin_permissions_router


admin_router = Router()
admin_router.add_router('/users', admin_users_router)
admin_router.add_router('/roles', admin_roles_router)
admin_router.add_router('/permissions', admin_permissions_router)
