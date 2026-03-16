import uuid
from datetime import date
from typing import List, Optional

from ninja import Schema, ModelSchema

from routes.models import Route
from seasons_sailings.models import Sailing, Season

from ships_cabins.models import Ship


class SailingOut(ModelSchema):
    class Meta:
        model = Sailing
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

class SailingIn(Schema):
    season: uuid.UUID
    ship: uuid.UUID
    route: Optional[uuid.UUID] = None
    departure_date: date
    nights: int

class OverlapSailingOut(ModelSchema):
    overlap_start: date
    overlap_end: date

    class Meta:
        model = Sailing
        fields = ['id', 'departure_date', 'nights']

class ValidateOverlapSailingsIn(Schema):
    ship: uuid.UUID
    departure_date: date
    nights: int
    exclude_sailing_id: Optional[uuid.UUID] = None
    season: Optional[uuid.UUID] = None

class ValidateOverlapSailingsOut(Schema):
    is_valid: bool
    overlaps: List[OverlapSailingOut]

class SailingSummaryOut(ModelSchema):
    class Meta:
        model = Sailing
        fields = ['id', 'departure_date', 'nights']

class ShipSummaryOut(ModelSchema):
    class Meta:
        model = Ship
        fields = ['id', 'name']

class SeasonSummaryOut(ModelSchema):
    class Meta:
        model = Season
        fields = ['id', 'name']

class RouteSummaryOut(ModelSchema):
    class Meta:
        model = Route
        fields = ['id', 'name']

class SummaryOut(Schema):
    sailing: SailingSummaryOut
    ship: ShipSummaryOut
    season: SeasonSummaryOut
    route: RouteSummaryOut

