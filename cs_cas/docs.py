SESSION_TAG_DESC = """
Relates all endpoints pertaining to sign-in and logged-in user sessions. This includes login flow,
reset password flow, and session authentication.

Note that a verification context is a cached record of relevant user information that is used to establish their
session once verification is complete.

The entire login flow is as follows:

1. email+password+optional remember_me → `/api/auth/login`: returns verification context id + default 2FA method/device.
    If the method is None, the user has not setup a 2FA device yet.
    - A user may setup a TOTP device or SMS device (the device must match their `twofa_method`, i.e a user with
          `twofa_method='sms'` cannot setup a TOTP device)
        - SMS setup through `/api/auth/2fa/sms/send`
2. context id+purpose (login/reset) → /api/auth/2fa/sms/send: sends OTP
3. passcode+purpose (login/reset) → /api/auth/2fa/verify: establishes login session
"""

TAG_GROUPS = [
    {"name": "A. Authentication & Profile", "tags": ["A1. Login / 2FA / Forgotten Password",
                                                     "A2. My Profile"]},
    {"name": "B. Admin: Users & Roles", "tags": ["B1. Users",
                                                 "B2. Roles",
                                                 "B3. Permissions"]},
    {"name": "C. Catalogues", "tags": ["C1. Amenities",
                                       "C2. Cabin Categories",
                                       "C3. Custom Costs",
                                       "C4. FX",
                                       "C5. Reserve Settings",
                                       "C6. Cancellation Policies"]},
    {"name": "D. Ships, Cabins & Cabin Maps", "tags": ["D1. Ships",
                                                       "D2. Cabin Maps",
                                                       "D3. Cabins"]},
    {"name": "E. Routes (Google Places)", "tags": ["Routes", "Ports"]},
    {"name": "F. Seasons & Sailings", "tags": ["Seasons", "Sailings"]},
]

TAGS = [
    {"name": "A1. Login / 2FA / Forgotten Password", "description": SESSION_TAG_DESC},
]