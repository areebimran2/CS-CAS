from django.contrib.auth import get_user_model
from ninja import Schema
from enum import Enum


# TFA endpoint schemas
class UnAuthPurpose(str, Enum):
    # Represents purposes that correspond to unauthenticated actions
    # Add more OTP purposes as needed
    LOGIN = 'login'


class TFAMethod(str, Enum):
    SMS = 'sms'
    TOTP = 'totp'


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
    # purpose: UnAuthPurpose


class TFAConfirmOut(Schema):
    id: str
    message: str


class TFAVerifyIn(Schema):
    id: str
    passcode: str
    # purpose: UnAuthPurpose

