import uuid

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from common.schemas import ReasonIn
from myadmin.schemas import UserIn, UserOut
from myadmin.services import users as service

router = Router(tags=['B1. Users'])
User = get_user_model()


@router.get('', response=NinjaPaginationResponseSchema[UserOut])
@requires('users.view')
@paginate()
def list_users(request):
    """
    Returns the users in the system.
    """
    return User.objects.all()


@router.post('', response=UserOut)
@requires('users.create')
def create_user(request, payload: UserIn):
    """
    Creates a user with their preferences and role.
    """
    return service.create_user(**payload.dict())


@router.get('/{user_id}', response=UserOut)
@requires('users.view')
def get_user(request, user_id: uuid.UUID):
    """
    Returns a user.
    """
    return get_object_or_404(User, id=user_id)


@router.put('/{user_id}', response=UserOut)
@requires('users.edit')
def update_user(request, payload: PatchDict[UserIn], user_id: uuid.UUID):
    """
    Updates a user. Only the fields sent are changed; a new `role_id` replaces the user's role.
    """
    user = get_object_or_404(User, id=user_id)
    return service.update_user(user, payload)


@router.post('/{user_id}/suspend', response=UserOut)
@requires('users.suspend')
def suspend_user(request, payload: ReasonIn, user_id: uuid.UUID):
    """
    Suspends a user, which blocks their sign-ins and ends their sessions without deleting their history.
    """


@router.post('/{user_id}/unsuspend', response=UserOut)
@requires('users.suspend')
def unsuspend_user(request, payload: ReasonIn, user_id: uuid.UUID):
    """
    Reactivates a suspended user.
    """


@router.delete('/{user_id}', response={204: None})
@requires('users.delete')
def delete_user(request, user_id: uuid.UUID):
    """
    Deletes a user that nothing refers to (no holds, bookings or other records). Otherwise responds 409 `IN_USE`;
    suspend the user instead.
    """
