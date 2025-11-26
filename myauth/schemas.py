from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema
from enum import Enum

from typing import Optional

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from myauth.models import UserPreference


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
    remember_me: Optional[bool] = False


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


class TokenOut(Schema):
    access: str


class ForgotPasswordIn(Schema):
    email: EmailStr


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
    CHANGE_TFA_METHOD = 'change-tfa-method'


class TFAMethod(str, Enum):
    SMS = 'sms'
    TOTP = 'totp'


class SecuritySetupIn(Schema):
    purpose: AuthPurpose


class VerifySchema(Schema):
    passcode: str


class ChangePhoneIn(Schema):
    phone: PhoneNumber


class ChangePasswordIn(Schema):
    passcode: str
    new_password: str


class ChangeEmailIn(Schema):
    passcode: str
    email: EmailStr


class ChangeTFAMethodIn(Schema):
    passcode: str
    method: TFAMethod


# User info endpoint schemas
class UserPrefSchema(ModelSchema):
    class Meta:
        model = UserPreference
        fields = ['opt_in_enabled', 'notify_cabin_avail', 'notify_flash_sale', 'notify_release_request', 'fx_mode']
        fields_optional = '__all__'

class UserSchema(ModelSchema):
    preferences: UserPrefSchema

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'middle_name', 'last_name', 'designation', 'email', 'phone', 'twofa_method', 'twofa_enabled']
        fields_optional = ['middle_name']

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone)


class UserUpdateSchema(ModelSchema):
    preferences: Optional[UserPrefSchema] = None

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'middle_name', 'last_name', 'designation']
        fields_optional = '__all__'


# Miscellaneous schemas
class MessageOut(Schema):
    message: str
