from typing import List, Optional

from ninja import ModelSchema, Schema
from pydantic import model_validator

from common.exceptions import ValidationFailedError
from myadmin.models import Permission, Role


class RoleIn(Schema):
    name: str
    description: Optional[str] = None
    permissions: List[str]

    @model_validator(mode='after')
    def permissions_exist(self):
        if self.permissions is None:  # partial update (PatchDict) that doesn't change the permissions
            return self
        existing = set(Permission.objects.filter(key__in=self.permissions).values_list('key', flat=True))
        missing = sorted(set(self.permissions) - existing)
        if missing:
            raise ValidationFailedError(
                detail='One or more permissions are invalid',
                errors=[{'field': 'permissions', 'message': f'No permission with key {key}'} for key in missing],
            )
        return self


class RoleOut(ModelSchema):
    permissions: List[str]

    class Meta:
        model = Role
        fields = ['id', 'name', 'description']

    @staticmethod
    def resolve_permissions(obj):
        return obj.permissions.values_list('key', flat=True)
