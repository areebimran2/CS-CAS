from django.db import transaction

from common.services import update_instance
from myadmin.models import Permission, Role


@transaction.atomic
def create_role(*, permissions: list[str], **fields) -> Role:
    role = Role.objects.create(**fields)
    role.permissions.set(Permission.objects.filter(key__in=permissions))
    return role


@transaction.atomic
def update_role(role: Role, changes: dict) -> Role:
    """Apply a partial update. A permission list, if given, replaces all of the role's permissions."""
    changes = dict(changes)
    if (permissions := changes.pop('permissions', None)) is not None:
        role.permissions.set(Permission.objects.filter(key__in=permissions))
    return update_instance(role, changes)
