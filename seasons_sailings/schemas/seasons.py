import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated, List, Optional

from ninja import ModelSchema, Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field

from common.schemas import ArchivedFilter, NonEmptyStr
from seasons_sailings.models import Season

Margin = Annotated[Decimal, Field(ge=0, max_digits=6, decimal_places=4, description='0.15 means 15%')]

# -- Requests


class SeasonIn(Schema):
    name: NonEmptyStr
    start_date: date
    end_date: date = Field(description='Inclusive. Seasons may not overlap.')
    default_margin_b2b: Margin
    default_margin_b2c: Margin


class SeasonShipsIn(Schema):
    ship_ids: List[uuid.UUID]


class SeasonFilter(ArchivedFilter):
    search: Annotated[Optional[str], FilterLookup('name__icontains')] = None


class ValidateOverlapSeasonsIn(Schema):
    start_date: date
    end_date: date
    exclude_season_id: Optional[uuid.UUID] = Field(default=None, description='The season being edited')


# -- Responses

class SeasonOut(ModelSchema):
    ship_ids: List[uuid.UUID]

    class Meta:
        model = Season
        fields = ['id', 'name', 'start_date', 'end_date', 'default_margin_b2b', 'default_margin_b2c', 'is_archived']


class OverlapSeasonOut(ModelSchema):
    overlap_start: date
    overlap_end: date

    class Meta:
        model = Season
        fields = ['id', 'name', 'start_date', 'end_date']


class ValidateOverlapSeasonsOut(Schema):
    is_valid: bool
    overlaps: List[OverlapSeasonOut]
