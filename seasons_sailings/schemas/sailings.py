import uuid
from datetime import date
from typing import Annotated, List, Optional

from ninja import FilterSchema, ModelSchema, Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field

from routes.models import Route
from seasons_sailings.models import Sailing, Season
from ships_cabins.models import Ship

# -- Requests


class SailingIn(Schema):
    season_id: uuid.UUID
    ship_id: uuid.UUID
    route_id: Optional[uuid.UUID] = None
    departure_date: date
    nights: int = Field(gt=0, description="The ship can't have another sailing in these nights")


class SailingBulkIn(Schema):
    sailings: List[SailingIn] = Field(min_length=1, max_length=500)


class SailingFilter(FilterSchema):
    season_id: Optional[uuid.UUID] = None
    ship_id: Annotated[Optional[List[uuid.UUID]], FilterLookup('ship_id__in')] = None
    route_id: Optional[uuid.UUID] = None
    departure_from: Annotated[Optional[date], FilterLookup('departure_date__gte')] = None
    departure_to: Annotated[Optional[date], FilterLookup('departure_date__lte')] = None
    nights: Optional[int] = None


class ValidateOverlapSailingsIn(Schema):
    ship_id: uuid.UUID
    departure_date: date
    nights: int = Field(gt=0)
    season_id: Optional[uuid.UUID] = Field(default=None, description='To check the "ends after the season" warning')
    exclude_sailing_id: Optional[uuid.UUID] = Field(default=None, description='The sailing being edited')


# -- Responses

class SailingOut(Schema):
    id: uuid.UUID
    season_id: uuid.UUID
    ship_id: uuid.UUID
    route_id: Optional[uuid.UUID]
    departure_date: date
    nights: int


class OverlapSailingOut(ModelSchema):
    overlap_start: date
    overlap_end: date

    class Meta:
        model = Sailing
        fields = ['id', 'departure_date', 'nights']


class ValidateOverlapSailingsOut(Schema):
    is_valid: bool
    overlaps: List[OverlapSailingOut]
    ends_after_season: bool = Field(description='A warning only: the sailing can still be saved')


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
    route: Optional[RouteSummaryOut]  # sailings don't need a route
