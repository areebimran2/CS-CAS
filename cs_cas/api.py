"""
Mounts every app's routers under /api. Paths have no trailing slash: /api/ships, /api/ships/{ship_id}.
Sections follow the spec's modules.
"""
from ninja import NinjaAPI, Redoc

from catalogs.api import catalogs_router, fx_router, policies_router
from common.access import DenyUndeclared
from common.exceptions import APIErrorManager
from cs_cas.docs import TAG_GROUPS, TAGS
from discounts.api import discounts_router
from import_export.api import exports_router, import_templates_router, imports_router
from myadmin.api import admin_router
from myauth.api import auth_router, me_router
from pricing.api import pricing_router
from reports.api import audit_router, report_schedules_router, reports_router
from routes.api import places_router, routes_router
from seasons_sailings.api import sailings_router, seasons_router
from selling.api import bookings_router, holds_router, release_requests_router, zoho_router
from ships_cabins.api import ships_router

api = NinjaAPI(docs=Redoc(),
               openapi_extra={"tags": TAGS, "x-tagGroups": TAG_GROUPS},
               # Endpoints must declare who may use them (see common/access.py); undeclared ones refuse everyone.
               auth=DenyUndeclared(),
               )

APIErrorManager(api)

# A. Sign-in, two-factor and my profile (including dashboard layout and notification settings)
api.add_router('auth', auth_router)
api.add_router('me', me_router)

# B. Admin: users, roles and permissions
api.add_router('admin', admin_router)

# C. Catalogues: amenities, cabin categories, custom costs, FX, reserve and cancellation policies
api.add_router('catalog', catalogs_router)
api.add_router('fx', fx_router)
api.add_router('policies', policies_router)

# D. Ships, cabins and cabin maps
api.add_router('ships', ships_router)

# E. Routes (Google Places)
api.add_router('routes', routes_router)
api.add_router('places', places_router)

# F. Seasons and sailings
api.add_router('seasons', seasons_router)
api.add_router('sailings', sailings_router)

# G, H. Pricing and list pricing
api.add_router('pricing', pricing_router)

# I. Sell, reserve and book (Zoho UC Ref)
api.add_router('zoho', zoho_router)
api.add_router('holds', holds_router)
api.add_router('bookings', bookings_router)
api.add_router('release-requests', release_requests_router)

# J. Discounts and flash sales
api.add_router('discounts', discounts_router)

# K. Import and export
api.add_router('import-templates', import_templates_router)
api.add_router('imports', imports_router)
api.add_router('exports', exports_router)

# L. Reports, and Q. audit history
api.add_router('reports', reports_router)
api.add_router('report-schedules', report_schedules_router)
api.add_router('audit-log', audit_router)
