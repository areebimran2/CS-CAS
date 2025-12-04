from ninja import Router

from common.utils import not_implemented
from myauth.models import UserPreference, UserRole
from myadmin.schemas import *

router = Router(tags=['Users'])
User = get_user_model()

@router.get('')
def list_users(request):
    return not_implemented()


@router.post('', response=CreateUserOut)
def create_user(request, payload: CreateUserIn):
    payload_dict = payload.dict()
    role_id = payload_dict.pop('role_id')
    user = User.objects.create(**payload_dict)
    UserPreference.objects.create(user=user)
    UserRole.objects.create(user=user, role_id=role_id)
    return user


@router.put('/{user_id}')
def update_user(request, user_id: str):
    return not_implemented()

@router.post('/{user_id}/suspend')
def suspend_user(request, user_id: str):
    return not_implemented()