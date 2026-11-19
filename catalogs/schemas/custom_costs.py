from ninja import ModelSchema, Schema

from catalogs.models import CustomCost
from common.enums import CustomCostAppliesTo, CustomCostMode


class CustomCostIn(Schema):
    key: str
    label: str
    mode: CustomCostMode
    applies_to: CustomCostAppliesTo
    is_active: bool


class CustomCostOut(ModelSchema):
    mode: CustomCostMode
    applies_to: CustomCostAppliesTo

    class Meta:
        model = CustomCost
        fields = ['id', 'key', 'label', 'is_active']
