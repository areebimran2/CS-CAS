import uuid

from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from myadmin.models import Role
from myadmin.schemas import RoleIn, RoleOut
from myadmin.services import roles as service

router = Router(tags=['B2. Roles'])


@router.get('', response=NinjaPaginationResponseSchema[RoleOut])
@requires('roles.view')
@paginate()
def list_roles(request):
    """
    Returns a list of roles, and their assigned permissions.
    """
    return Role.objects.all()


@router.post('', response=RoleOut)
@requires('roles.create')
def create_role(request, payload: RoleIn):
    """
    Create a new role along with its associated permissions.
    """
    return service.create_role(**payload.dict())


@router.put('/{role_id}', response=RoleOut)
@requires('roles.edit')
def update_role(request, payload: PatchDict[RoleIn], role_id: uuid.UUID):
    """
    Update an existing role's details, including its associated permissions.
    """
    return service.update_role(get_object_or_404(Role, id=role_id), payload)

@router.get('/{role_id}', response=RoleOut)
@requires('roles.view')
def get_role(request, role_id: uuid.UUID):
    """
    Retrieve a specific role by its ID.
    """
    role = get_object_or_404(Role, id=role_id)
    return role
