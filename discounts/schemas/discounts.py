import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Optional

from ninja import FilterSchema, Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field

from common.enums import DiscountKind, DiscountStatus, DiscountTargetKind, SalesChannel
from common.schemas import NonEmptyStr

MarginFloor = Annotated[Decimal, Field(ge=0, max_digits=6, decimal_places=4, description='0.05 means 5%')]


# -- Requests

class DiscountTargetIn(Schema):
    target_kind: DiscountTargetKind
    target_id: uuid.UUID = Field(description='The id of the sailing, cabin category or cabin')


class DiscountIn(Schema):
    name: NonEmptyStr
    kind: DiscountKind
    value: Decimal = Field(gt=0, max_digits=10, decimal_places=4, description='0.20 means 20% for percent discounts')
    channel: SalesChannel = SalesChannel.BOTH
    starts_at: datetime
    ends_at: datetime
    min_margin_b2b: MarginFloor = Decimal('0.05')
    min_margin_b2c: MarginFloor = Decimal('0.10')
    targets: List[DiscountTargetIn] = Field(min_length=1, description='The most specific target wins: cabin, '
                                                                     'then category, then sailing')


class DiscountFilter(FilterSchema):
    status: Annotated[Optional[List[DiscountStatus]], FilterLookup('status__in')] = None
    channel: Optional[SalesChannel] = None
    search: Annotated[Optional[str], FilterLookup('name__icontains')] = None


# -- Responses

class DiscountTargetOut(Schema):
    target_kind: DiscountTargetKind
    target_id: uuid.UUID


class DiscountOut(Schema):
    id: uuid.UUID
    name: str
    kind: DiscountKind
    value: Decimal
    channel: SalesChannel
    starts_at: datetime
    ends_at: datetime
    min_margin_b2b: Decimal
    min_margin_b2c: Decimal
    status: DiscountStatus
    targets: List[DiscountTargetOut]
