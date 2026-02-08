import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Literal

from ninja import Schema, ModelSchema
from pydantic import Field

from discounts.models import Discount, DiscountTarget

class DiscountKind(str, Enum):
    PERCENT = 'percent'
    FIXED = 'fixed'

class DiscountChannel(str, Enum):
    B2B = 'b2b'
    B2C = 'b2c'
    BOTH = 'both'

class DiscountStatus(str, Enum):
    SCHEDULED = 'scheduled'
    ACTIVE = 'active'
    ENDED = 'ended'
    CANCELLED = 'cancelled'

class DiscountTargetKind(str, Enum):
    SAILING = 'sailing'
    CATEGORY = 'category'
    CABIN = 'cabin'

class DiscountTargetOut(ModelSchema):
    target_kind: DiscountTargetKind

    class Meta:
        model = DiscountTarget
        fields = ['sailing', 'category', 'cabin']

class DiscountOut(ModelSchema):
    targets: List[DiscountTargetOut]
    kind: DiscountKind
    channel: DiscountChannel
    status: DiscountStatus

    class Meta:
        model = Discount
        fields = '__all__'
        exclude = ['created_at', 'kind', 'channel', 'status']

class DiscountTargetIn(Schema):
    target_kind: DiscountTargetKind
    id: uuid.UUID

class DiscountIn(Schema):
    name: str
    kind: DiscountKind
    value: Decimal = Field(max_digits=10, decimal_places=4)
    channel: DiscountChannel
    starts_at: datetime
    ends_at: datetime
    min_margin_b2b: Optional[Decimal] = Field(max_digits=6, decimal_places=4)
    max_margin_b2c: Optional[Decimal] = Field(max_digits=6, decimal_places=4)
    targets: List[DiscountTargetIn]

class DiscountActivateOut(ModelSchema):
    status: Literal[DiscountStatus.ACTIVE]

    class Meta:
        model = Discount
        fields = ['id']

class DiscountDeactivateOut(ModelSchema):
    status: Literal[DiscountStatus.CANCELLED]

    class Meta:
        model = Discount
        fields = ['id']