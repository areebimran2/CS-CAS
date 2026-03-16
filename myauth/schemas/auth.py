from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema

from typing import Optional

from pydantic import EmailStr


# Login endpoint schemas
class Method(Schema):
    name: str
    type: str

    @staticmethod
    def resolve_type(obj):
        return obj.__class__.__name__


class LoginIn(Schema):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class LoginOut(Schema):
    id: str
    method: Optional[Method] = None


class TokenOut(Schema):
    access: str


class ForgotPasswordIn(Schema):
    email: EmailStr


class ResetPasswordIn(Schema):
    id: str
    token: str
    password: str


# Miscellaneous schemas
class MessageOut(Schema):
    message: str

