import uuid
from typing import List, Dict, Optional

from ninja import Schema, ModelSchema
from pydantic import FileUrl
from pydantic_extra_types.currency_code import Currency

from ships_cabins.models import Ship


class ShipIn(Schema):
    name: str
    operator: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[Dict] = None
    currencies: List[Currency]
    amenities: Optional[List[uuid.UUID]] = None
    photo_gallery: Optional[List[FileUrl]] = None

class ShipOut(ModelSchema):
    currencies: List[Currency]
    photo_gallery: List[FileUrl]

    class Meta:
        model = Ship
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

class ShipUpdateIn(Schema):
    name: Optional[str] = None
    operator: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[Dict] = None

class ShipCurrenciesIn(Schema):
    currencies: List[Currency]


class ShipAmenitiesIn(Schema):
    amenities: List[uuid.UUID]


class ShipPhotoIn(Schema):
    url: FileUrl

