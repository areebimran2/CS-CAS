import uuid
from typing import Optional, List

from django.contrib.auth import authenticate, get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user
from ninja import Router, Schema
from ninja.errors import AuthenticationError
from ninja_jwt.schema import TokenObtainPairOutputSchema

router = Router()
User = get_user_model()

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

@router.post('/login', response=LoginOut)
def login(request, data: LoginIn):
    user: Optional[User] = authenticate(username=data.email, password=data.password)
    if user is None:
        AuthenticationError()

    devices = list(devices_for_user(user))

    return {'id': user.id, 'methods': devices}

@router.post('/2fa/setup')
def setup_2fa(request):
    pass

@router.post('/2fa/verify')
def verify_2fa(request):
    pass