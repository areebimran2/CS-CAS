from typing import Optional

from ninja import Schema, ModelSchema

from catalogs.models import CabinCategory


class CabinCategoryIn(Schema):
    name: str
    sort_order: Optional[int] = 100
    is_active: bool


class CabinCategoryOut(ModelSchema):
    class Meta:
        model = CabinCategory
        fields = ['id', 'name', 'sort_order', 'is_active']

