import uuid
from typing import Optional, List

from ninja import Schema, ModelSchema
from pydantic_extra_types.coordinate import Latitude, Longitude

from routes.models import Route, RouteLeg


class RouteLegOut(ModelSchema):
    class Meta:
        model = RouteLeg
        fields = '__all__'
        exclude = ['route']

class RouteOut(ModelSchema):
    leg_count: int

    class Meta:
        model = Route
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

    @staticmethod
    def resolve_leg_count(obj):
        return obj.routeleg_set.count()

class RouteOutWithLegs(ModelSchema):
    legs: List[RouteLegOut]

    class Meta:
        model = Route
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

    @staticmethod
    def resolve_legs(obj):
        return obj.routeleg_set.order_by('seq').all()


class RouteLegIn(Schema):
    seq: int
    place_id: str
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None

class RouteIn(Schema):
    name: Optional[str] = None
    notes: Optional[str] = None
    legs: List[RouteLegIn]

class RouteLegUpdateIn(Schema):
    place: uuid.UUID
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None

class RouteLegReorderIn(Schema):
    order: List[uuid.UUID]

class PlacePrediction(Schema):
    place_id: str
    description: str

class PlacesPredictionsOut(Schema):
    predictions: List[PlacePrediction]

class PlaceDetailsOut(Schema):
    place_id: str
    name: str
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None
