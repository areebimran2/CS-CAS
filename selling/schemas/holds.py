import uuid
from datetime import datetime
from typing import Optional

from ninja import FilterSchema, Schema
from pydantic import Field

from common.enums import HoldStatus, ReleaseDecision
from common.schemas import NonEmptyStr, OptionalStr


# -- Requests

class HoldIn(Schema):
    sailing_id: uuid.UUID
    cabin_id: uuid.UUID
    uc_ref: NonEmptyStr
    notes: OptionalStr = None
    expires_at: Optional[datetime] = Field(
        default=None,
        description='Replaces the expiry the reserve policy gives. Needs `selling.override_hold_expiry`',
    )


class HoldFilter(FilterSchema):
    sailing_id: Optional[uuid.UUID] = None
    cabin_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    status: Optional[HoldStatus] = None
    uc_ref: Optional[str] = None


class ReleaseRequestFilter(FilterSchema):
    hold_id: Optional[uuid.UUID] = None
    requested_by_id: Optional[uuid.UUID] = None


# -- Responses

class HoldOut(Schema):
    id: uuid.UUID
    sailing_id: uuid.UUID
    cabin_id: uuid.UUID
    user_id: uuid.UUID
    uc_ref: str
    status: HoldStatus
    expires_at: datetime
    created_at: datetime


class ReleaseRequestOut(Schema):
    id: uuid.UUID
    hold_id: uuid.UUID
    requested_by_id: uuid.UUID
    reason: Optional[str]
    created_at: datetime


class ReleaseRequestResultOut(Schema):
    id: uuid.UUID
    result: ReleaseDecision
    hold: HoldOut = Field(description='The hold after the decision: released when approved, unchanged when denied')
