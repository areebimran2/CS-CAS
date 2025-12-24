from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.utils import not_implemented
from myadmin.models import Role, Permission
from myadmin.schemas import RoleOut, RoleIn
from myauth.schemas import *

router = Router(tags=['Roles'])
User = get_user_model()


@router.get('', response=NinjaPaginationResponseSchema[RoleOut])
@paginate()
def list_roles(request):
    return Role.objects.all()


@router.post('', response=RoleOut)
def create_role(request, payload: RoleIn):
    payload_dict = payload.dict()
    permissions = payload_dict.pop('permissions')
    role = Role.objects.create(**payload_dict)                  # Create the Role
    perms_qs = Permission.objects.filter(key__in=permissions)   # Obtain permissions queryset
    role.permissions.set(perms_qs)                              # Establish role-permission relationships
    return role


@router.put('/{role_id}')
def update_role(request, role_id: str):
    return not_implemented()

@router.get('/{role_id}', response=RoleOut)
def get_role(request, role_id: str):
    role = get_object_or_404(Role, id=role_id)
    return role