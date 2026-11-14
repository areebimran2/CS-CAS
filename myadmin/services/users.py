from django.contrib.auth import get_user_model
from django.db import transaction

from common.services import update_instance
from myadmin.models import Role
from myauth.services.password import validate_user_password

User = get_user_model()


@transaction.atomic
def create_user(*, password: str, role_id, **fields) -> User:
    """Create a user with their preferences (made by the user manager) and their single role."""
    validate_user_password(password)
    user = User.objects.create_user(password=password, **fields)
    user.roles.set([role_id])
    return user


@transaction.atomic
def update_user(user: User, changes: dict) -> User:
    """Apply a partial update. A new password is validated and hashed; a new role replaces the current one."""
    changes = dict(changes)
    if (password := changes.pop('password', None)) is not None:
        validate_user_password(password, user=user)
        user.set_password(password)
    if (role_id := changes.pop('role_id', None)) is not None:
        user.roles.set([Role.objects.get(id=role_id)])
    return update_instance(user, changes)
