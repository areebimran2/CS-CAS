import uuid
from typing import Optional

from ninja import Header, Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from common.schemas import ReasonIn
from selling.schemas import HoldFilter, HoldIn, HoldOut, ReleaseRequestOut

router = Router(tags=['I2. Holds'])


@router.get('', response=NinjaPaginationResponseSchema[HoldOut])
@requires('selling.view')
@paginate()
def list_holds(request, filters: Query[HoldFilter]):
    """
    Returns holds, newest first, filtered by sailing, cabin, holder, status or UC Ref.
    """


@router.post('', response=HoldOut)
@requires('selling.reserve')
def create_hold(request, payload: HoldIn,
                idempotency_key: Optional[str] = Header(default=None, alias='Idempotency-Key')):
    """
    Reserves a cabin on a sailing. The expiry comes from the reserve settings, and reminder emails are scheduled before
    it. Responds 409 `HOLD_EXISTS` when someone else holds the cabin (request a release instead) and 409
    `CABIN_BOOKED` when it's booked. Repeating a request with the same `Idempotency-Key` returns the first hold.
    """


@router.get('/{hold_id}', response=HoldOut)
@requires('selling.view')
def get_hold(request, hold_id: uuid.UUID):
    """
    Returns a hold.
    """


@router.post('/{hold_id}/extend', response=HoldOut)
@requires('selling.reserve')
def extend_hold(request, hold_id: uuid.UUID):
    """
    Extends an active hold by the reserve settings' extension time, if extensions are allowed and the hold hasn't
    used them all.
    """


@router.post('/{hold_id}/release', response=HoldOut)
@requires('selling.reserve')
def release_hold(request, hold_id: uuid.UUID):
    """
    Releases an active hold early, freeing the cabin. Holders release their own holds; admins can release any.
    """


@router.post('/{hold_id}/release-request', response=ReleaseRequestOut)
@requires('selling.reserve')
def create_release_request(request, payload: ReasonIn, hold_id: uuid.UUID):
    """
    Asks the holder to release a hold on a cabin the signed-in user wants. The holder is notified and can approve or
    deny it under `/api/release-requests`.
    """
