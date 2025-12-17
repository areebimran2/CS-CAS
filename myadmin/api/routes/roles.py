from ninja import Router

from common.utils import not_implemented
from myadmin.models import Role
from myauth.schemas import *

router = Router(tags=['Roles'])
User = get_user_model()


@router.get('')
def list_roles(request):
    return Role.objects.all()


@router.post('')
def create_role(request):
    return not_implemented()

@router.put('/{role_id}')
def update_role(request, role_id: str):
    return not_implemented()