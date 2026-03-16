from enum import Enum

from ninja import Schema
from ninja_extra import status
from pydantic import EmailStr, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from common.exceptions import APIBaseError
from myauth.schemas.tfa import TFAMethod


# Authenticated user OTP security schemas
class AuthPurpose(str, Enum):
    # Represents purposes that correspond to secure authenticated actions
    # Add more OTP purposes as needed
    VERIFY_OLD_PHONE = 'verify-old-phone'
    VERIFY_NEW_PHONE = 'verify-new-phone'
    CHANGE_EMAIL = 'change-email'
    CHANGE_PASSWORD = 'change-password'
    CHANGE_TFA_METHOD = 'change-tfa-method'


class SecuritySetupIn(Schema):
    purpose: AuthPurpose


class VerifySchema(Schema):
    passcode: str


class ChangePhoneIn(Schema):
    phone: PhoneNumber


class ChangePasswordIn(Schema):
    passcode: str
    password: str
    confirm: str

    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.confirm:
            raise APIBaseError(
                title='Password mismatch',
                detail='The given password and confirm password do not match',
                status=status.HTTP_400_BAD_REQUEST,
                errors=[{'field': 'confirm', 'message': 'Does not match given password'}],
            )
        return self


class ChangeEmailIn(Schema):
    passcode: str
    email: EmailStr


class ChangeTFAMethodIn(Schema):
    passcode: str
    method: TFAMethod

