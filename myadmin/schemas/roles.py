from typing import Optional, List

from ninja import Schema, ModelSchema
from ninja_extra import status
from pydantic import model_validator

from common.exceptions import APIBaseError
from myadmin.models import Role, Permission


class RoleIn(Schema):
    name: str
    description: Optional[str] = None
    permissions: List[str]

    @model_validator(mode='after')
    def permissions_exists(self):
        existing = set(Permission.objects.filter(key__in=self.permissions).values_list('key', flat=True))
        missing = set(self.permissions) - existing
        if missing:
            raise APIBaseError(
                title='Invalid permissions',
                detail='One or more permissions are invalid',
                status=status.HTTP_400_BAD_REQUEST,
                errors=[{'field': key, 'message': 'No permission with this key'} for key in missing],
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

