from django.contrib.auth import authenticate
from ninja import Router, Schema

router = Router()

class LoginSchema(Schema):
    email = str
    password = str

@router.post('/login', response=LoginSchema)
def login(request, data: LoginSchema):
    pass