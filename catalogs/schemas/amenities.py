from ninja import Schema, ModelSchema

from catalogs.models import Amenity


class AmenityIn(Schema):
    name: str
    is_active: bool


class AmenityOut(ModelSchema):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'is_active']

