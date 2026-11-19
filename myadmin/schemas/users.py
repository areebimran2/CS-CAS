import uuid
from typing import List, Optional

from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema
from pydantic import EmailStr, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from common.enums import UserStatus
from common.exceptions import ValidationFailedError
from myadmin.models import Role


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
        # role_id is None only in partial updates (PatchDict) that don't change the role
        if self.role_id is not None and not Role.objects.filter(id=self.role_id).exists():
            raise ValidationFailedError(errors=[{'field': 'role_id', 'message': 'No role with this id'}])
        return self


class UserRoleSchema(ModelSchema):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserOut(ModelSchema):
    roles: List[UserRoleSchema]  # Reverse reference to roles
    status: UserStatus

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'designation', 'email', 'phone']

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone)
