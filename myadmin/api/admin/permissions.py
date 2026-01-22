from ninja import Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from myadmin.models import Permission

from myadmin.schemas import PermissionOut

router = Router(tags=['B3. Permissions'])

@router.get('', response=NinjaPaginationResponseSchema[PermissionOut])
@paginate()
def list_permissions(request):
    """
    Provides a paginated list of the permissions catalogs.
    """
    return Permission.objects.all()