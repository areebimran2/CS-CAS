import uuid
from enum import Enum
from typing import Optional, List

from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema
from ninja_extra import status
from pydantic import EmailStr, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from common.exceptions import APIBaseError
from myadmin.models import Role, Permission


class Status(str, Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'

class UserIn(Schema):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    designation: str
    email: EmailStr
    phone: PhoneNumber
    password: str
    role_id: uuid.UUID

    @model_validator(mode='after')
    def validate_role(self):
        if not Role.objects.filter(id=self.role_id).exists():
            raise APIBaseError(
                title='Invalid role',
                detail='The specified role does not exist',
                status=status.HTTP_400_BAD_REQUEST,
                errors=[{'field': 'role_id', 'message': 'No role with this ID'}],
            )
        return self


class UserRoleSchema(ModelSchema):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserOut(ModelSchema):
    roles: List[UserRoleSchema]  # Reverse reference to roles
    status: Status

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'designation', 'email', 'phone']

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone)


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

class PermissionOut(ModelSchema):
    class Meta:
        model = Permission
        fields = ['key', 'description']

class MessageIn(Schema):
    text: Optional[str] = None