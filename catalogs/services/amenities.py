from django.db import transaction

from catalogs.models import Amenity
from common.services import update_instance


@transaction.atomic
def create_amenity(**fields) -> Amenity:
    return Amenity.objects.create(**fields)


@transaction.atomic
def update_amenity(amenity: Amenity, changes: dict) -> Amenity:
    return update_instance(amenity, changes)
