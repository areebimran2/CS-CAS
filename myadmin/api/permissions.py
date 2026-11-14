from ninja import Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from common.access import requires
from myadmin.models import Permission

from myadmin.schemas import PermissionOut

router = Router(tags=['B3. Permissions'])

@router.get('', response=NinjaPaginationResponseSchema[PermissionOut])
@requires('roles.view')
@paginate()
def list_permissions(request):
    """
    Returns a list of the permissions catalogs.
    """
    return Permission.objects.all()