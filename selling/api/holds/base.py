from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from selling.schemas import *

router = Router(tags=['I2. Reserve'])

@router.get('', response=NinjaPaginationResponseSchema[HoldOut])
@paginate()
def list_holds(request):
    """
    Returns a list of holds.
    """

@router.get('/{hold_id}', response=HoldOut)
def get_hold(request, hold_id):
    """
    Returns a single holds details.
    """

@router.post('', response=HoldOut)
def create_hold(request, payload: HoldIn):
    """
    Creates a new hold (reserve a cabin) with an expiry computed from the reserve policy (reserve_settings).
    """

@router.post('/{hold_id}/extend', response=HoldExtensionOut)
def extend_hold(request, hold_id):
    """
    Extends a cabin hold expiry if the global reserve policy (reserve_settings) permits extensions.

    Returns the updated cabin hold.
    """

@router.post('/{hold_id}/release', response=HoldReleaseOut)
def release_hold(request, hold_id):
    """
    Releases a cabin hold early (freeing the cabin).

    Note: supports "owner releases" and admin releases
    """

@router.post('/{hold_id}/release=request', response=ReleaseRequestOut)
def release_request_hold(request, payload: ReasonIn, hold_id):
    """
    Creates a release request when a cabin is held by another user. In other words, allows other users to request
    release from the holder.
    """