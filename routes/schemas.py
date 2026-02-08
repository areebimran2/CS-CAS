import uuid
from typing import Optional, List

from ninja import Schema, ModelSchema
from pydantic_extra_types.coordinate import Latitude, Longitude

from routes.models import Route, RouteLeg


class RouteOut(ModelSchema):
    class Meta:
        model = Route
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

class RouteIn(Schema):
    name: Optional[str] = None
    notes: Optional[str] = None

class RouteLegOut(ModelSchema):
    class Meta:
        model = RouteLeg
        fields = '__all__'
        exclude = ['route']

class RouteLegIn(Schema):
    place: uuid.UUID
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None
    seq: Optional[int] = None

class RouteLegUpdateIn(Schema):
    place: uuid.UUID
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None

class RouteLegReorderIn(Schema):
    order: List[uuid.UUID]

class PlaceOut(Schema):
    place_id: str
    display_text: str

class PlaceDetailsOut(Schema):
    place_id: str
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None
