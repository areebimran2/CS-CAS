import uuid
from typing import Optional

from ninja import ModelSchema, Schema
from pydantic import HttpUrl

from common.enums import MapAssetKind, MapStatus
from common.schemas import OptionalStr
from ships_cabins.models import CabinMap, CabinMapZone

# -- Requests


class CabinMapIn(Schema):
    notes: OptionalStr = None


class CabinMapUpdateIn(Schema):
    """Notes, and the asset uploaded through the upload URL endpoint (SVG, or a JPG/PNG to draw zones on)."""
    notes: OptionalStr = None
    svg_url: Optional[HttpUrl] = None
    raster_url: Optional[HttpUrl] = None


class UploadUrlIn(Schema):
    kind: MapAssetKind
    filename: str


class CabinZoneIn(Schema):
    cabin_id: uuid.UUID
    polygon: dict


class CabinZoneReplaceIn(Schema):
    zones: list[CabinZoneIn]


class CabinZoneUpdateIn(Schema):
    cabin_id: Optional[uuid.UUID] = None
    polygon: Optional[dict] = None


# -- Responses

class CabinZoneOut(ModelSchema):
    cabin_id: uuid.UUID

    class Meta:
        model = CabinMapZone
        fields = ['id', 'polygon']


class CabinMapOut(ModelSchema):
    status: MapStatus
    zones: list[CabinZoneOut]

    class Meta:
        model = CabinMap
        fields = ['id', 'version', 'svg_url', 'raster_url', 'notes']


class UploadUrlOut(Schema):
    upload_url: HttpUrl
    asset_url: HttpUrl


class CabinZoneReplaceOut(Schema):
    updated: int


class DetectedZoneOut(Schema):
    """A region found in the SVG, with the cabin whose number matches its label, if any."""
    label: Optional[str]
    polygon: dict
    suggested_cabin_id: Optional[uuid.UUID] = None


class CabinMapActivateOut(Schema):
    activated_map: uuid.UUID
    previous_map: Optional[uuid.UUID] = None  # None when the ship had no active map
