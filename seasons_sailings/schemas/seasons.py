import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

from ninja import Schema, ModelSchema

from seasons_sailings.models import Season

from pydantic import Field


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

