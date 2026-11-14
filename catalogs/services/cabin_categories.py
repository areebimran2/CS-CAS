from django.db import transaction

from catalogs.models import CabinCategory
from common.services import update_instance


@transaction.atomic
def create_cabin_category(**fields) -> CabinCategory:
    return CabinCategory.objects.create(**fields)


@transaction.atomic
def update_cabin_category(category: CabinCategory, changes: dict) -> CabinCategory:
    return update_instance(category, changes)
