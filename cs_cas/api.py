from ninja import NinjaAPI, Redoc

from common.exceptions import APIErrorManager
from cs_cas.docs import TAG_GROUPS, TAGS
from myauth.api import auth_router, me_router
from myadmin.api import admin_router
from catalogs.api import catalogs_router, fx_router, policies_router
from ships_cabins.api import ships_router
from routes.api import routes_router
from seasons_sailings.api import seasons_router, sailings_router
from pricing.api import pricing_router
from selling.api import selling_router, holds_router, bookings_router, release_requests_router
from discounts.api import discounts_router
from import_export.api import import_templates_router, imports_router, exports_router
from reports.api import reports_router

api = NinjaAPI(docs=Redoc(),
               openapi_extra={"tags": TAGS, "x-tagGroups": TAG_GROUPS},
               )

APIErrorManager(api)

# A. Sign-in, Two-Factor & My Profile
api.add_router('auth/', auth_router)
api.add_router('me/', me_router)

# B. Admin: Users, Roles & Permissions
api.add_router('admin/', admin_router)

# C. Catalogues: Amenities, Categories, Custom Costs, FX, Reserve & Cancellation
api.add_router('catalog/', catalogs_router)
api.add_router('fx/', fx_router)
api.add_router('policies/', policies_router)

# D. Ships, Cabins & Interactive Cabin Maps
api.add_router('ships/', ships_router)

# E. Routes (Google Places)
api.add_router('routes/', routes_router)

# F. Seasons & Sailings
api.add_router('seasons/', seasons_router)
api.add_router('sailings/', sailings_router)

# (G. + H.) Pricing (Cost of Ship by Season/Sailing) and List Pricing (Totals & Drill-down)
api.add_router('pricing/', pricing_router)

# I. Sell / Reserve / Book (Zoho UC Ref)
api.add_router('selling/', selling_router)
api.add_router('holds/', holds_router)
api.add_router('bookings/', bookings_router)
api.add_router('release-requests/', release_requests_router)

# J. Discounts & Flash Sales
api.add_router('discounts/', discounts_router)

# K. Import / Export
api.add_router('import-templates/', import_templates_router)
api.add_router('imports/', imports_router)
api.add_router('exports/', exports_router)

# L. Reports & Analytics
api.add_router('reports/', reports_router)