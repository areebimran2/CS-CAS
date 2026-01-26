from django.shortcuts import get_object_or_404
from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.utils import not_implemented
from myadmin.models import Role, Permission
from myadmin.schemas import RoleOut, RoleIn
from myauth.schemas import *

router = Router(tags=['B2. Roles'])
User = get_user_model()


@router.get('', response=NinjaPaginationResponseSchema[RoleOut])
@paginate()
def list_roles(request):
    """
    Returns a list of roles, and their assigned permissions.
    """
    return Role.objects.all()


@router.post('', response=RoleOut)
def create_role(request, payload: RoleIn):
    """
    Create a new role along with its associated permissions.
    """
    payload_dict = payload.dict()
    permissions = payload_dict.pop('permissions')
    role = Role.objects.create(**payload_dict)                  # Create the Role
    perms_qs = Permission.objects.filter(key__in=permissions)   # Obtain permissions queryset
    role.permissions.set(perms_qs)                              # Establish role-permission relationships
    return role


@router.put('/{role_id}', response=RoleOut)
def update_role(request, payload: PatchDict[RoleIn], role_id: str):
    """
    Update an existing role's details, including its associated permissions.
    """
    role = Role.objects.get(id=role_id)

    data = dict(payload)
    perms= data.pop('permissions', None)

    # Update role permission set if role_id is provided
    # Note: The given permission set will replace ALL existing permissions
    if perms is not None:
        perms_qs = Permission.objects.filter(key__in=perms)
        role.permissions.set(perms_qs)

    for attr, value in data.items():
        setattr(role, attr, value)

    role.save()

    return role

@router.get('/{role_id}', response=RoleOut)
def get_role(request, role_id: str):
    """
    Retrieve a specific role by its ID.
    """
    role = get_object_or_404(Role, id=role_id)
    return role