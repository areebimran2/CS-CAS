import uuid
from enum import Enum
from typing import List, Dict, Optional

from ninja import Schema, ModelSchema
from pydantic import FileUrl, HttpUrl

from ships_cabins.models import CabinMap, CabinMapZone


class MapStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'

class UploadKind(str, Enum):
    SVG = 'svg'
    RASTER = 'raster'

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

