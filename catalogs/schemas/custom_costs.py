from enum import Enum

from ninja import Schema, ModelSchema

from pricing.models import CustomCost


class Mode(str, Enum):
    FIXED = 'fixed'
    PERCENT = 'percent'


class AppliesTo(str, Enum):
    PER_CABIN = 'per_cabin'
    PER_PAX = 'per_pax'


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

