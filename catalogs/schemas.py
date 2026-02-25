from enum import Enum
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List

from ninja import Schema, ModelSchema
from pydantic_extra_types.currency_code import Currency

from catalogs.models import Amenity, CabinCategory
from pricing.models import CustomCost
from fx.models import ExchangeRatesManual, FXRatesCache
from selling.models import ReserveSetting, CancellationPolicy, CancellationPolicyTier

from pydantic import Field


class Mode(str, Enum):
    FIXED = 'fixed'
    PERCENT = 'percent'

class AppliesTo(str, Enum):
    PER_CABIN = 'per_cabin'
    PER_PAX = 'per_pax'

class Status(str, Enum):
    OK = 'ok'
    DEGRADED = 'degraded'
    DOWN = 'down'

class ChargeType(str, Enum):
    PERCENT_TOTAL = 'percent_total'
    PERCENT_COS = 'percent_cos'
    FIXED_AMOUNT = 'fixed_amount'


class AmenityIn(Schema):
    name: str
    is_active: bool

class AmenityOut(ModelSchema):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'is_active']

class CabinCategoryIn(Schema):
    name: str
    sort_order: Optional[int] = 100
    is_active: bool

class CabinCategoryOut(ModelSchema):
    class Meta:
        model = CabinCategory
        fields = ['id', 'name', 'sort_order', 'is_active']

class CustomCostIn(Schema):
    key: str
    label: str
    mode: Mode
    applies_to: AppliesTo
    is_active: bool

class CustomCostOut(ModelSchema):
    mode: Mode
    applies_to: AppliesTo

    class Meta:
        model = CustomCost
        fields = ['id', 'key', 'label', 'is_active']

class ManualFXIn(Schema):
    base: Currency
    quote: Currency
    rate: Decimal = Field(max_digits=18, decimal_places=8)

class ManualFXOut(ModelSchema):
    class Meta:
        model = ExchangeRatesManual
        fields = '__all__'
        exclude = ['id']

class ManualFXInList(Schema):
    rates: List[ManualFXIn]

class QuoteOut(ModelSchema):
    is_stale: bool

    class Meta:
        model = FXRatesCache
        fields = ['rate', 'fetched_at']

class LiveFXOut(ModelSchema):
    quotes: List[QuoteOut]

    class Meta:
        model = FXRatesCache
        fields = ['provider', 'base']

class RefreshLiveFXIn(Schema):
    base: str
    quotes: List[str]

class CacheStatusOut(Schema):
    provider: str
    last_refresh_at: datetime
    stale_after_hours: int
    status: Status

class ReserveSettingsIn(Schema):
    max_hold_minutes: int
    reminder_scheduled_minutes: List[int]
    allow_extensions: Optional[bool] = True
    max_extensions: Optional[int] = 1
    extension_minutes: Optional[int] = 1440

class ReserveSettingsOut(ModelSchema):
    class Meta:
        model = ReserveSetting
        fields = '__all__'
        exclude = ['created_at', 'created_by']

class CancellationPolicyTierIn(Schema):
    min_days: int
    max_days: int
    charge_type: ChargeType
    value: Decimal = Field(max_digits=10, decimal_places=4)

class CancellationPolicyTierOut(ModelSchema):
    charge_type: ChargeType

    class Meta:
        model = CancellationPolicyTier
        fields = '__all__'
        exclude = ['policy', 'charge_type']

class CancellationPolicyIn(Schema):
    name: str
    non_refundable: bool
    tiers: List[CancellationPolicyTierIn]

class CancellationPolicyOut(ModelSchema):
    tiers: List[CancellationPolicyTierOut]

    class Meta:
        model = CancellationPolicy
        fields = '__all__'
        exclude = ['created_at']

class MoneyOut(Schema):
    amount: Decimal = Field(decimal_places=2)
    currency: Currency

class QuoteCancellationChargeIn(Schema):
    departure_date: date
    today: date
    total: MoneyOut
    cos: MoneyOut

class QuoteCancellationChargeOut(Schema):
    days_out: int
    tier: CancellationPolicyTierOut
    clamped_to_total: bool
