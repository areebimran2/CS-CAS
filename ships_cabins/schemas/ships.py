import uuid
from typing import List, Annotated, Optional

from ninja import ModelSchema, Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field, field_validator
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.currency_code import Currency

from catalogs.models import Amenity
from common.schemas import ArchivedFilter, NonEmptyStr, OptionalStr
from ships_cabins.models import Ship, ShipPhoto


class Address(Schema):
    """A postal address, used in requests and responses. Stored in the ship's `address` JSON column."""
    line1: NonEmptyStr
    line2: OptionalStr = None
    city: NonEmptyStr
    region: OptionalStr = None
    postal_code: OptionalStr = None
    country: CountryAlpha2  # ISO 3166-1 alpha-2, e.g. HR


# -- Requests

class ShipIn(Schema):
    name: NonEmptyStr
    operator: OptionalStr = None
    contact_person: OptionalStr = None
    address: Optional[Address] = None
    currencies: List[Currency] = Field(min_length=1)
    amenity_ids: List[uuid.UUID] = []
    new_amenities: List[NonEmptyStr] = Field(default=[], description='Names to add to the amenity master list')

    @field_validator('currencies', 'amenity_ids', 'new_amenities')
    @classmethod
    def remove_duplicates(cls, values):
        return list(dict.fromkeys(values))


class ShipFilter(ArchivedFilter):
    search: Annotated[Optional[str], FilterLookup(['name__icontains', 'operator__icontains'])] = None


class PhotoIn(Schema):
    id: uuid.UUID
    sort_order: int


class ReorderPhotoIn(Schema):
    order: List[PhotoIn]


class UploadFileIn(Schema):
    filename: str
    content_type: str


class PhotoUploadUrlsIn(Schema):
    files: List[UploadFileIn]


# -- Responses

class AmenityOut(ModelSchema):
    class Meta:
        model = Amenity
        fields = ['id', 'name']


class PhotoOut(ModelSchema):
    class Meta:
        model = ShipPhoto
        fields = ['id', 'url', 'sort_order']


class ListPhotoOut(Schema):
    photos: List[PhotoOut]


class ShipOut(ModelSchema):
    address: Optional[Address] = None
    currencies: List[Currency]
    amenities: List[AmenityOut]
    photos: List[PhotoOut]

    class Meta:
        model = Ship
        fields = ['id', 'name', 'operator', 'contact_person', 'is_archived']

    @staticmethod
    def resolve_currencies(ship):
        return ship.shipcurrency_set.values_list('currency', flat=True)

    @staticmethod
    def resolve_photos(ship):
        return ship.shipphoto_set.order_by('sort_order', 'created_at')


class ShipDetailOut(ShipOut):
    """Read from services.ships.ships_with_summary(), which adds the counts."""
    cabin_count: int
    active_map_version: Optional[int] = None


class ShipListOut(ModelSchema):
    """Read from services.ships.ships_with_summary(), which adds the counts in the same query."""
    currencies: List[Currency]
    amenity_count: int
    cabin_count: int
    photo_count: int
    active_map_version: Optional[int] = None

    class Meta:
        model = Ship
        fields = ['id', 'name', 'operator', 'is_archived']

    @staticmethod
    def resolve_currencies(ship):
        return [row.currency for row in ship.shipcurrency_set.all()]  # prefetched, so no query per ship


class UploadFileOut(Schema):
    upload_url: str
    asset_url: str


class PhotoUploadUrlsOut(Schema):
    files: List[UploadFileOut]
