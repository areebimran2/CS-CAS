from ninja import Router

from common.utils import not_implemented
from myauth.schemas import *

router = Router(tags=['Users'])
User = get_user_model()

@router.get('')
def list_users(request):
    return not_implemented()


@router.post('')
def create_user(request):
    return not_implemented()

@router.put('/{user_id}')
def update_user(request, user_id: str):
    return not_implemented()

@router.post('/{user_id}/suspend')
def suspend_user(request, user_id: str):
    return not_implemented()