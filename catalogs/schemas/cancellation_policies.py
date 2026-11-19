from datetime import date
from decimal import Decimal
from typing import List

from ninja import ModelSchema, Schema
from pydantic import Field

from catalogs.models import CancellationPolicy, CancellationPolicyTier
from common.enums import CancellationChargeType
from common.schemas import Money


class CancellationPolicyTierIn(Schema):
    min_days: int
    max_days: int
    charge_type: CancellationChargeType
    value: Decimal = Field(max_digits=10, decimal_places=4, description='Percent charge types use 0..1')


class CancellationPolicyTierOut(ModelSchema):
    charge_type: CancellationChargeType

    class Meta:
        model = CancellationPolicyTier
        fields = '__all__'
        exclude = ['policy', 'charge_type']


class CancellationPolicyIn(Schema):
    name: str
    non_refundable: bool = False
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
    total: Money
    cos: Money


class QuoteCancellationChargeOut(Schema):
    days_out: int
    tier: CancellationPolicyTierOut
    charge: Money
