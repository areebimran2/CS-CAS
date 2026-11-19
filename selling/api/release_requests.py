import uuid

from ninja import Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from selling.schemas import ReleaseRequestFilter, ReleaseRequestOut, ReleaseRequestResultOut

router = Router(tags=['I5. Release Requests'])


@router.get('', response=NinjaPaginationResponseSchema[ReleaseRequestOut])
@requires('selling.view')
@paginate()
def list_release_requests(request, filters: Query[ReleaseRequestFilter]):
    """
    Returns release requests, newest first. Create one with `POST /api/holds/{hold_id}/release-request`.
    """


@router.get('/{request_id}', response=ReleaseRequestOut)
@requires('selling.view')
def get_release_request(request, request_id: uuid.UUID):
    """
    Returns a release request.
    """


@router.post('/{request_id}/approve', response=ReleaseRequestResultOut)
@requires('selling.reserve')
def approve_release_request(request, request_id: uuid.UUID):
    """
    Approves a release request: the hold is released in the same transaction and the requester is notified.
    """


@router.post('/{request_id}/deny', response=ReleaseRequestResultOut)
@requires('selling.reserve')
def deny_release_request(request, request_id: uuid.UUID):
    """
    Denies a release request. The hold stays and the requester is notified.
    """
