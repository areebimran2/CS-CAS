import uuid

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from myadmin.schemas import MessageIn, UserIn, UserOut
from myadmin.services import users as service

router = Router(tags=['B1. Users'])
User = get_user_model()


@router.get('', response=NinjaPaginationResponseSchema[UserOut])
@requires('users.view')
@paginate()
def list_users(request):
    """
    Returns a list users in the system.
    """
    return User.objects.all()


@router.post('', response=UserOut)
@requires('users.create')
def create_user(request, payload: UserIn):
    """
    Create a new user along with their preferences and role association.
    """
    return service.create_user(**payload.dict())


@router.put('/{user_id}', response=UserOut)
@requires('users.edit')
def update_user(request, payload: PatchDict[UserIn], user_id: uuid.UUID):
    """
    Update an existing user's details, including password and role association.
    """
    return service.update_user(get_object_or_404(User, id=user_id), payload)


@router.get('/{user_id}', response=UserOut)
@requires('users.view')
def get_user(request, user_id: uuid.UUID):
    """
    Retrieve detailed information about a specific user by their ID.
    """
    user = get_object_or_404(User, id=user_id)
    return user


@router.post('/{user_id}/suspend', response=UserOut)
@requires('users.suspend')
def suspend_user(request, payload: MessageIn, user_id: uuid.UUID):
    """
    Suspend a user account, disabling their access to the system.
    """
    # user = get_object_or_404(User, id=user_id)
    # user.is_active(False)
    #
    # # TODO: Need to clear user sessions and related cached records (pending actions, OTPs, etc.)
    #
    # user.save()
    # return user

@router.post('/{user_id}/unsuspend', response=UserOut)
@requires('users.suspend')
def unsuspend_user(request, payload: MessageIn, user_id: uuid.UUID):
    """
    Reactivate a user account, granting their access to the system.
    """
