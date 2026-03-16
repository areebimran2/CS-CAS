import uuid
from typing import Optional

from ninja import Schema, ModelSchema

from ships_cabins.models import Cabin


class CabinOut(ModelSchema):
    class Meta:
        model = Cabin
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

class CabinIn(Schema):
    name: str
    number: str
    deck: Optional[str] = None
    category: uuid.UUID

