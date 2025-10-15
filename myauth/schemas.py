from ninja import Schema
from enum import Enum

from typing import Optional
import uuid

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
class Purpose(str, Enum):
    # Add more OTP purposes as needed
    LOGIN = 'login'


class TFASetupIn(Schema):
    id: uuid.UUID
    purpose: Purpose

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
    purpose: Purpose

class TFAVerifyOut(Schema):
    access: str
    refresh: str