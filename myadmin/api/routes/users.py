from django.shortcuts import get_object_or_404
from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.utils import not_implemented, validate_user_password
from myauth.models import UserPreference
from myadmin.models import UserRole
from myadmin.schemas import *

router = Router(tags=['Users'])
User = get_user_model()

@router.get('', response=NinjaPaginationResponseSchema[UserOut])
@paginate()
def list_users(request):
    return User.objects.all()


@router.post('', response=UserOut)
def create_user(request, payload: UserIn):
    payload_dict = payload.dict()
    role_id = payload_dict.pop('role_id')
    validate_user_password(payload_dict['password'])    # Validate password
    user = User.objects.create(**payload_dict)          # Create the user
    UserPreference.objects.create(user=user)            # Create user preferences
    UserRole.objects.create(user=user, role_id=role_id) # Establish user-role relationship
    return user


@router.put('/{user_id}', response=UserOut)
def update_user(request, payload: PatchDict[UserIn], user_id: str):
    user = User.objects.get(id=user_id)
    validate_user_password(payload['password'], user=user)

    data = dict(payload)
    role_id = data.pop('role_id')

    # Update user-role relationship if role_id is provided
    if role_id is not None:
        user_role = get_object_or_404(UserRole, user=user)
        user_role.role_id = role_id
        user_role.save()

    for attr, value in data.items():
        setattr(user, attr, value)

    user.save()

    return user

@router.post('/{user_id}/suspend')
def suspend_user(request, user_id: str):
    return not_implemented()