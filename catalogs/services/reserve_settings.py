from django.db import transaction

from catalogs.models import ReserveSetting
from common.services import update_instance


def current_reserve_settings() -> ReserveSetting:
    """The reserve policy in force: the most recent row (one is created by the seed migration)."""
    return ReserveSetting.objects.order_by('-created_at').first()


@transaction.atomic
def update_reserve_settings(changes: dict) -> ReserveSetting:
    return update_instance(current_reserve_settings(), changes)
