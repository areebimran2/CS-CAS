import uuid
from datetime import datetime

from ninja import Schema
from pydantic import HttpUrl


class PushKeys(Schema):
    p256dh: str
    auth: str


class PushSubscriptionIn(Schema):
    """A browser's Web Push subscription, as returned by `PushManager.subscribe()` (spec P, VAPID)."""
    endpoint: HttpUrl
    keys: PushKeys


class PushSubscriptionOut(Schema):
    id: uuid.UUID
    endpoint: HttpUrl
    created_at: datetime


class VapidKeyOut(Schema):
    public_key: str
