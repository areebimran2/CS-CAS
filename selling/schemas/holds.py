import uuid
from enum import Enum
from typing import Optional

from ninja import Schema, ModelSchema

from selling.models import Hold, ReleaseRequest


class HoldStatus(str, Enum):
    ACTIVE = 'active'
    RELEASED = 'released'
    EXPIRED = 'expired'
    CONVERTED = 'converted'


class HoldOut(ModelSchema):
    status: HoldStatus

    class Meta:
        model = Hold
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'idempotency_key', 'status']

class HoldIn(Schema):
    sailing: uuid.UUID
    cabin: uuid.UUID
    uc_ref: str
    notes: Optional[str] = None

class HoldExtensionOut(ModelSchema):
    status: HoldStatus

    class Meta:
        model = Hold
        fields = ['id', 'expires_at']

class ReasonIn(Schema):
    reason: Optional[str] = None

class HoldReleaseOut(Schema):
    status: HoldStatus

    class Meta:
        model = Hold
        fields = ['id']


class RequestStatus(str, Enum):
    APPROVED = 'approved'
    DENIED = 'denied'


class ReleaseRequestOut(ModelSchema):
    class Meta:
        model = ReleaseRequest
        fields = '__all__'

class ReleaseRequestResult(ModelSchema):
    result: RequestStatus

    class Meta:
        model = ReleaseRequest
        fields = ['id']

