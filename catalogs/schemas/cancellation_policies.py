from decimal import Decimal
from datetime import date
from enum import Enum
from typing import List, Optional

from ninja import Schema, ModelSchema
from pydantic_extra_types.currency_code import Currency

from selling.models import CancellationPolicy, CancellationPolicyTier

from pydantic import Field


class ChargeType(str, Enum):
    PERCENT_TOTAL = 'percent_total'
    PERCENT_COS = 'percent_cos'
    FIXED_AMOUNT = 'fixed_amount'


class MoneyOut(Schema):
    amount: Decimal = Field(decimal_places=2)
    currency: Currency


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
    non_refundable: Optional[bool] = None
    tiers: List[CancellationPolicyTierIn] = Field(min_length=1)


class CancellationPolicyOut(ModelSchema):
    tiers: List[CancellationPolicyTierOut]

    class Meta:
        model = CancellationPolicy
        fields = '__all__'
        exclude = ['created_at']

    @staticmethod
    def resolve_tiers(obj):
        return obj.cancellationpolicytier_set.all()


class QuoteCancellationChargeIn(Schema):
    departure_date: date
    today: date
    total: MoneyOut
    cos: MoneyOut


class QuoteCancellationChargeOut(Schema):
    days_out: int
    tier: CancellationPolicyTierOut
    charge: MoneyOut

