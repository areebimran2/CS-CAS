import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from ninja import Schema, ModelSchema

from routes.models import Route
from seasons_sailings.models import Season, Sailing

from pydantic import Field

from selling.models import Hold, Booking
from ships_cabins.models import Ship, Cabin

class CabinStatus(str, Enum):
    AVAILABLE = 'available'
    RESERVED = 'reserved'
    BOOKED = 'booked'


class SeasonOut(ModelSchema):
    class Meta:
        model = Season
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

class SeasonIn(Schema):
    name: str
    start_date: date
    end_date: date
    default_margin_b2b: Decimal = Field(max_digits=6, decimal_places=4)
    default_margin_b2c: Decimal = Field(max_digits=6, decimal_places=4)

class AssignShips(Schema):
    ships: List[uuid.UUID]

class OverlapSeasonOut(ModelSchema):
    overlap_start: date
    overlap_end: date

    class Meta:
        model = Season
        fields = ['id', 'name', 'start_date', 'end_date']

class ValidateOverlapSeasonsIn(Schema):
    start_date: date
    end_date: date
    exclude_season_id: Optional[uuid.UUID] = None

class ValidateOverlapSeasonsOut(Schema):
    is_valid: bool
    overlaps: List[OverlapSeasonOut]

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
    overlaps: List[OverlapSeasonOut]

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

class HoldAvailabilityOut(ModelSchema):
    class Meta:
        model = Hold
        fields = ['id', 'uc_ref', 'expires_at']

class BookingAvailabilityOut(ModelSchema):
    class Meta:
        model = Booking
        fields = ['id', 'uc_ref']

class CabinAvailabilityOut(Schema):
    cabin: uuid.UUID
    status: CabinStatus
    hold: Optional[HoldAvailabilityOut] = None
    booking: Optional[BookingAvailabilityOut] = None
