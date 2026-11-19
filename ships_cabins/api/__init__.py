from .cabin_maps import router as cabin_maps_router
from .cabins import router as cabins_router
from .ships import router as ships_router

# Cabins and cabin maps belong to a ship, so they're mounted on the ships router: /ships/{ship_id}/cabins.
# (Mounting the ships router itself at '' under another router would give /ships/ a trailing slash.)
ships_router.add_router('{ship_id}/cabin-maps', cabin_maps_router)
ships_router.add_router('{ship_id}/cabins', cabins_router)

__all__ = ['ships_router']
