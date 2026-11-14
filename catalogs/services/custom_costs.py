from django.db import transaction

from catalogs.models import CustomCost
from common.services import update_instance


@transaction.atomic
def create_custom_cost(**fields) -> CustomCost:
    return CustomCost.objects.create(**fields)


@transaction.atomic
def update_custom_cost(custom_cost: CustomCost, changes: dict) -> CustomCost:
    return update_instance(custom_cost, changes)
