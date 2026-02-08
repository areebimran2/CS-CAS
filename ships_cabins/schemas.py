import uuid
from enum import Enum
from typing import List, Dict, Optional

from ninja import Schema, ModelSchema
from pydantic import FileUrl, HttpUrl
from pydantic_extra_types.currency_code import Currency

from ships_cabins.models import Ship, Cabin, CabinMap, CabinMapZone


class MapStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'

class UploadKind(str, Enum):
    SVG = 'svg'
    RASTER = 'raster'

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

class CabinZoneOut(ModelSchema):
    class Meta:
        model = CabinMapZone
        fields = '__all__'
        exclude = ['map']

class CabinZoneIn(Schema):
    cabin: uuid.UUID
    polygon: Dict


class CabinMapOut(ModelSchema):
    zones: List[CabinZoneOut]
    status: MapStatus

    class Meta:
        model = CabinMap
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'status']

class CabinMapIn(Schema):
    notes: Optional[str] = None

class UploadUrlIn(Schema):
    kind: UploadKind
    filename: str

class UploadUrlOut(Schema):
    upload_url: HttpUrl
    asset_url: FileUrl

class CabinMapUpdateIn(Schema):
    notes: Optional[str] = None
    svg_url: Optional[FileUrl] = None
    raster_url: Optional[FileUrl] = None

class CabinZoneReplaceIn(Schema):
    zones: List[CabinZoneIn]

class CabinZoneReplaceOut(Schema):
    updated: int

class CabinZoneUpdateIn(Schema):
    polygon: Optional[Dict] = None
    cabin: Optional[uuid.UUID] = None

class CabinMapActivateOut(Schema):
    activated_map: uuid.UUID
    previous_map: uuid.UUID