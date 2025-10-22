from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema
from enum import Enum

from typing import Optional
import uuid

from pydantic_extra_types.phone_numbers import PhoneNumber


# Login endpoint schemas
class Method(Schema):
    name: str
    type: str

    @staticmethod
    def resolve_type(obj):
        return obj.__class__.__name__


class LoginIn(Schema):
    email: str
    password: str


class LoginOut(Schema):
    id: str
    method: Optional[Method] = None


# TFA endpoint schemas
class UnAuthPurpose(str, Enum):
    # Represents purposes that correspond to unauthenticated actions
    # Add more OTP purposes as needed
    LOGIN = 'login'
    RESET_PASSWORD = 'reset-password'

class TFASetupTOTPIn(Schema):
    id: str

class TFASetupTOTPOut(Schema):
    id: str
    otpauth_url: str

class TFAConfirmTOTPIn(Schema):
    id: str
    url: str
    passcode: str

class TFASetupSMSIn(Schema):
    id: str
    purpose: UnAuthPurpose

class TFAConfirmOut(Schema):
    id: str
    message: str

class TFAVerifyIn(Schema):
    id: str
    passcode: str
    purpose: UnAuthPurpose

class TFAVerifyOut(Schema):
    access: str
    refresh: str

class ForgotPasswordIn(Schema):
    email: str

class ResetPasswordIn(Schema):
    id: str
    token: str
    new_password: str
    passcode: str

# Authenticated user OTP security schemas
class AuthPurpose(str, Enum):
    # Represents purposes that correspond to secure authenticated actions
    # Add more OTP purposes as needed
    VERIFY_OLD_PHONE = 'verify-old-phone'
    VERIFY_NEW_PHONE = 'verify-new-phone'
    CHANGE_EMAIL = 'change-email'
    CHANGE_PASSWORD = 'change-password'

class SecuritySetupIn(Schema):
    purpose: AuthPurpose

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