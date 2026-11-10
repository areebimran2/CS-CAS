import uuid
from typing import List, Dict, Optional

from ninja import Schema, ModelSchema
from pydantic_extra_types.currency_code import Currency

from catalogs.models import Amenity
from ships_cabins.models import Ship, ShipPhoto


class AddressIn(Schema):
    line1: str
    line2: str
    city: str
    region: str
    postal_one: str
    country_iso2: str

class ShipIn(Schema):
    name: str
    operator: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[Dict] = None
    currencies: List[Currency]
    amenities: Optional[List[uuid.UUID]] = []
    new_amenities: Optional[List[str]] = []

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
    currencies: List[Currency]
    amenities: List[AmenityOut]
    photos: List[PhotoOut]

    class Meta:
        model = Ship
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

    @staticmethod
    def resolve_currencies(obj):
        return obj.shipcurrency_set.all().values_list('currency', flat=True)

    @staticmethod
    def resolve_photos(obj):
        return obj.shipphoto_set.all().order_by('sort_order', 'created_at')

class ShipDetailOut(ShipOut):
    cabin_count: int
    active_map_version: Optional[int] = None

    @staticmethod
    def resolve_cabin_count(obj):
        return obj.cabin_set.filter(is_archived=False).count()

    @staticmethod
    def resolve_active_map_version(obj):
        active_map = obj.cabinmap_set.filter(status='active').first()
        return active_map.version if active_map else None

class ShipListOut(ModelSchema):
    currencies: List[Currency]
    amenity_count: int
    cabin_count: int
    photo_count: int
    active_map_version: Optional[int] = None

    class Meta:
        model = Ship
        fields = ['id', 'name', 'operator']

    @staticmethod
    def resolve_currencies(obj):
        return obj.shipcurrency_set.all().values_list('currency', flat=True)

    @staticmethod
    def resolve_amenity_count(obj):
        return obj.amenities.filter(is_active=True).count()

    @staticmethod
    def resolve_cabin_count(obj):
        return obj.cabin_set.filter(is_archived=False).count()

    @staticmethod
    def resolve_photo_count(obj):
        return obj.shipphoto_set.count()

    @staticmethod
    def resolve_active_map_version(obj):
        active_map = obj.cabinmap_set.filter(status='active').first()
        return active_map.version if active_map else None

class UploadFileIn(Schema):
    filename: str
    content_type: str

class UploadFileOut(Schema):
    upload_url: str
    asset_url: str

class PhotoUploadUrlsIn(Schema):
    files: List[UploadFileIn]

class PhotoUploadUrlsOut(Schema):
    files: List[UploadFileOut]

class PhotoIn(Schema):
    id: uuid.UUID
    sort_order: int

class ReorderPhotoIn(Schema):
    order: List[PhotoIn]

