from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .me import router as me_router
from .push_subscriptions import router as push_subscriptions_router
from .tfa import router as tfa_router

# Sub-resources are mounted on their parent's router: /auth/2fa/..., /me/dashboard.
# (Mounting a parent at '' under another router would give /me/ a trailing slash.)
auth_router.add_router('2fa', tfa_router)
me_router.add_router('dashboard', dashboard_router)
me_router.add_router('push-subscriptions', push_subscriptions_router)

__all__ = ['auth_router', 'me_router']
