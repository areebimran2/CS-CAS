"""
The catalogue of every permission in the system: key -> description.

This is the single source of truth. After `manage.py migrate`, the myadmin app copies it into the `permissions`
table (see myadmin/apps.py), where roles are granted permissions. `@requires(...)` only accepts keys listed here, so a
typo fails when the server starts.

Keys follow `<module>.<action>`, with the spec's verbs: view, create, edit (which includes archiving), delete (only
records nothing refers to), and specific actions such as `selling.cancel`.

To add a permission: add it here, use it in `@requires(...)`, and run `migrate`.
"""

PERMISSIONS = {
    # B. Admin: users, roles and permissions
    'users.view': 'View users',
    'users.create': 'Create users',
    'users.edit': 'Edit users, including their role and password',
    'users.suspend': 'Suspend and reactivate users',
    'users.delete': 'Delete users that nothing refers to',
    'roles.view': 'View roles and the permission catalogue',
    'roles.create': 'Create roles',
    'roles.edit': 'Edit roles and the permissions they grant',
    'roles.delete': 'Delete roles that no user has',

    # C. Catalogues: amenities, cabin categories, custom costs, FX, reserve and cancellation policies
    'catalogs.view': 'View amenities, cabin categories and custom costs',
    'catalogs.create': 'Create amenities, cabin categories and custom costs',
    'catalogs.edit': 'Edit and deactivate amenities, cabin categories and custom costs',
    'catalogs.delete': 'Delete amenities, cabin categories and custom costs that nothing refers to',
    'fx.view': 'View manual and live exchange rates',
    'fx.edit': 'Edit and delete manual exchange rates, and refresh live rates',
    'policies.view': 'View reserve settings and cancellation policies',
    'policies.create': 'Create cancellation policies',
    'policies.edit': 'Edit reserve settings and cancellation policies',
    'policies.delete': 'Delete cancellation policies that nothing refers to',

    # D. Ships, cabins and cabin maps
    'ships.view': 'View ships, cabins and cabin maps',
    'ships.create': 'Create ships, cabins and cabin maps',
    'ships.edit': 'Edit, archive and activate ships, cabins, cabin maps and ship photos',
    'ships.delete': 'Delete ships, cabins and draft cabin maps that nothing refers to',

    # E. Routes
    'routes.view': 'View routes',
    'routes.create': 'Create routes',
    'routes.edit': 'Edit routes, including looking up ports with Google Places',
    'routes.delete': 'Delete routes that no sailing uses',

    # F. Seasons and sailings
    'seasons.view': 'View seasons',
    'seasons.create': 'Create seasons',
    'seasons.edit': 'Edit and archive seasons, and assign their ships',
    'seasons.delete': 'Delete seasons that nothing refers to',
    'sailings.view': 'View sailings and their cabin availability',
    'sailings.create': 'Create sailings',
    'sailings.edit': 'Edit sailings',
    'sailings.delete': 'Delete sailings that nothing refers to',

    # G, H. Pricing and list pricing
    'pricing.view': 'View cabin pricing, totals and price breakdowns',
    'pricing.edit': 'Set bulk pricing, per-cabin overrides and the custom costs used by each ship',
    'pricing.override_margin': 'Override the default margins',

    # I. Sell, reserve and book
    'selling.view': 'View holds, bookings and release requests, and look up UC Refs',
    'selling.reserve': 'Create, extend and release holds, and handle release requests',
    'selling.override_hold_expiry': 'Set a hold expiry other than the one the reserve policy gives',
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

    # L. Reports
    'reports.view': 'Run and export reports',
    'reports.schedule': 'Schedule reports to be emailed',

    # O, P. Real-time updates, collaborative locking and notifications
    'realtime.subscribe': 'Subscribe to real-time updates',
    'lock.override': 'Override collaborative locks',
    'lock.view_names': 'See who holds a collaborative lock',
    'push.subscribe': 'Receive browser push notifications',

    # Q. Audit history
    'audit.view': 'View the audit history',
}
