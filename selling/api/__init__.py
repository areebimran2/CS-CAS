from ninja import Router

from .selling.base import router as selling_base_router
from .holds.base import router as holds_base_router
from .bookings.base import router as bookings_base_router
from .release_requests.base import router as release_requests_base_router

selling_router = Router()
selling_router.add_router('', selling_base_router)

holds_router = Router()
holds_router.add_router('', holds_base_router)

bookings_router = Router()
bookings_router.add_router('', bookings_base_router)

release_requests_router = Router()
release_requests_router.add_router('', release_requests_base_router)

