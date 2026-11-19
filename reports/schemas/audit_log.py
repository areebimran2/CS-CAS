import uuid
from datetime import datetime
from typing import Annotated, Any, Optional

from ninja import FilterSchema, Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field


class AuditLogFilter(FilterSchema):
    entity: Optional[str] = Field(default=None, description='e.g. pricing, discount, booking, user')
    entity_id: Optional[uuid.UUID] = None
    actor_id: Optional[uuid.UUID] = None
    action: Optional[str] = Field(default=None, description='e.g. create, update, archive, override')
    since: Annotated[Optional[datetime], FilterLookup('ts__gte')] = None
    until: Annotated[Optional[datetime], FilterLookup('ts__lt')] = None


class AuditLogOut(Schema):
    id: uuid.UUID
    entity: str
    entity_id: Optional[uuid.UUID]
    action: str
    before: Optional[Any]
    after: Optional[Any]
    actor_id: Optional[uuid.UUID]
    ts: datetime
