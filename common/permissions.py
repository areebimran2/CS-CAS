"""
The catalogue of every permission in the system: key -> description.

This is the single source of truth. After `manage.py migrate`, the myadmin app copies it into the `permissions`
table (see myadmin/apps.py), where roles are granted permissions. `@requires(...)` only accepts keys listed here, so a
typo fails when the server starts.

To add a permission: add it here, use it in `@requires(...)`, and run `migrate`.
"""

PERMISSIONS = {
    # B. Admin: users, roles and permissions
    'users.view': 'View users',
    'users.create': 'Create users',
    'users.edit': 'Edit users, including their role and password',
    'users.suspend': 'Suspend and reactivate users',
    'roles.view': 'View roles and the permission catalogue',
    'roles.create': 'Create roles',
    'roles.edit': 'Edit roles and the permissions they grant',

    # C. Catalogues: amenities, cabin categories, custom costs, FX, reserve and cancellation policies
    'catalogs.view': 'View amenities, cabin categories and custom costs',
    'catalogs.create': 'Create amenities, cabin categories and custom costs',
    'catalogs.edit': 'Edit amenities, cabin categories and custom costs',
    'fx.view': 'View manual and live exchange rates',
    'fx.edit': 'Edit manual exchange rates and refresh live rates',
    'policies.view': 'View reserve settings and cancellation policies',
    'policies.create': 'Create cancellation policies',
    'policies.edit': 'Edit reserve settings and cancellation policies',

    # D. Ships, cabins and cabin maps
    'ships.view': 'View ships, cabins and cabin maps',
    'ships.create': 'Create ships, cabins and cabin maps',
    'ships.edit': 'Edit ships, cabins, cabin maps and ship photos',

    # E. Routes
    'routes.view': 'View routes',
    'routes.create': 'Create routes',
    'routes.edit': 'Edit routes, including looking up ports with Google Places',

    # F. Seasons and sailings
    'seasons.view': 'View seasons',
    'seasons.create': 'Create seasons',
    'seasons.edit': 'Edit seasons and the ships assigned to them',
    'sailings.view': 'View sailings and their cabin availability',
    'sailings.create': 'Create sailings',
    'sailings.edit': 'Edit sailings',

    # G, H. Pricing and list pricing
    'pricing.view': 'View cabin pricing and totals',
    'pricing.edit': 'Set bulk pricing and per-cabin overrides',
    'pricing.override_margin': 'Override the default margins',

    # I. Sell, reserve and book
    'selling.view': 'View holds, bookings and release requests, and look up UC Refs',
    'selling.reserve': 'Create, extend and release holds, and handle release requests',
    'selling.book': 'Create bookings',
    'selling.cancel': 'Cancel bookings',

    # J. Discounts and flash sales
    'discounts.view': 'View discounts',
    'discounts.create': 'Create discounts',
    'discounts.edit': 'Edit discounts',
    'discounts.activate': 'Activate or deactivate discounts',

    # K. Import and export
    'data.import': 'Import data from CSV files',
    'data.export': 'Export data to CSV or PDF',

    # O. Real-time updates and collaborative locking
    'realtime.subscribe': 'Subscribe to real-time updates',
    'lock.override': 'Override collaborative locks',
}
