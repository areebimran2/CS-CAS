from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema
from enum import Enum

from typing import Optional
import uuid

from pydantic_extra_types.phone_numbers import PhoneNumber


# Login endpoint schemas
class Method(Schema):
    persistent_id: str
    name: str
    type: str

    @staticmethod
    def resolve_type(obj):
        return obj.__class__.__name__


class LoginIn(Schema):
    email: str
    password: str


class LoginOut(Schema):
    id: uuid.UUID
    method: Optional[Method] = None


# TFA endpoint schemas
class TFASetupIn(Schema):
    id: uuid.UUID


class TFAConfirmTOTPIn(Schema):
    id: uuid.UUID
    url: str
    passcode: str


class TFASetupTOTPOut(Schema):
    id: uuid.UUID
    otpauth_url: str


class TFAConfirmOut(Schema):
    id: uuid.UUID
    device_id: str
    message: str


class TFAVerifyIn(Schema):
    id: uuid.UUID
    device_id: str
    passcode: str


class TFAVerifyOut(Schema):
    access: str
    refresh: str

# Authenticated user OTP security schemas
class Purpose(str, Enum):
    # Represents purposes that correspond to secure authenticated actions
    # Add more OTP purposes as needed
    VERIFY_OLD_PHONE = 'verify-old-phone'
    VERIFY_NEW_PHONE = 'verify-new-phone'
    CHANGE_EMAIL = 'change-email'
    CHANGE_PASSWORD = 'change-password'
    FORGOT_PASSWORD = 'forgot-password'

class SecuritySetupIn(Schema):
    purpose: Purpose

class VerifySchema(Schema):
    passcode: str

class ChangePhoneIn(Schema):
    phone: PhoneNumber

# User info endpoint schemas
class UserSchema(ModelSchema):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'middle_name', 'last_name', 'designation', 'email', 'phone', 'twofa_method']
        fields_optional = ['middle_name']

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone)

class UserBasicUpdateSchema(ModelSchema):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'middle_name', 'last_name', 'designation']

# Miscellaneous schemas
class MessageOut(Schema):
    message: str