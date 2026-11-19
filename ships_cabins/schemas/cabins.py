import uuid
from typing import Annotated, Optional

from ninja import Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field

from common.schemas import ArchivedFilter, NonEmptyStr, OptionalStr

# -- Requests


class CabinIn(Schema):
    number: NonEmptyStr = Field(description='Unique on the ship, ignoring case')
    name: OptionalStr = Field(default=None, description='Defaults to "Cabin <number>"')
    deck: OptionalStr = None
    category_id: uuid.UUID
    notes: OptionalStr = None


class CabinBulkIn(Schema):
    cabins: list[CabinIn] = Field(min_length=1, max_length=500)


class CabinFilter(ArchivedFilter):
    deck: Optional[str] = None
    category_id: Annotated[Optional[list[uuid.UUID]], FilterLookup('category_id__in')] = None
    search: Annotated[Optional[str], FilterLookup(['number__icontains', 'name__icontains'])] = None


# -- Responses

class CabinCategoryRef(Schema):
    id: uuid.UUID
    name: str


class CabinOut(Schema):
    id: uuid.UUID
    ship_id: uuid.UUID
    number: str
    name: str
    deck: Optional[str]
    category: CabinCategoryRef
    notes: Optional[str]
    is_archived: bool


class DeckOut(Schema):
    deck: str
    cabin_count: int
