from ninja import Schema

from typing import List
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
    methods: List[Method]

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