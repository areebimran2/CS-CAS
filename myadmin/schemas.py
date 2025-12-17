import uuid
from enum import Enum
from typing import Optional, List

from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema
from ninja.orm import register_field
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from myadmin.models import Role


class Status(str, Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'


register_field('PostgresEnumField', Status)


class UserIn(Schema):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    phone: PhoneNumber
    password: str
    role_id: uuid.UUID
    status: Status


class UserRoleSchema(ModelSchema):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserOut(ModelSchema):
    roles: List[UserRoleSchema]  # Reverse reference to roles

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'designation',
                  'email', 'phone', 'status', 'created_at', 'updated_at']

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone)
