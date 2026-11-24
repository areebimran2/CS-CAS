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
    Returns the roles and the permissions each grants.
    """
    return Role.objects.all()


@router.post('', response=RoleOut)
@requires('roles.create')
def create_role(request, payload: RoleIn):
    """
    Creates a role with the permissions it grants.
    """
    return service.create_role(**payload.dict())


@router.get('/{role_id}', response=RoleOut)
@requires('roles.view')
def get_role(request, role_id: uuid.UUID):
    """
    Returns a role.
    """
    return get_object_or_404(Role, id=role_id)


@router.put('/{role_id}', response=RoleOut)
@requires('roles.edit')
def update_role(request, payload: PatchDict[RoleIn], role_id: uuid.UUID):
    """
    Updates a role. Only the fields sent are changed; a `permissions` list replaces all of the role's permissions.
    """
    role = get_object_or_404(Role, id=role_id)
    return service.update_role(role, payload)


@router.delete('/{role_id}', response={204: None})
@requires('roles.delete')
def delete_role(request, role_id: uuid.UUID):
    """
    Deletes a role that no user has. Otherwise responds 409 `IN_USE`.
    """
