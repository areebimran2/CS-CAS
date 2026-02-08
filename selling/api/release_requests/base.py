from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from selling.schemas import ReleaseRequestOut, ReleaseRequestResult

router = Router(tags=['I5. Release Request (against a Hold)'])

@router.get('', response=NinjaPaginationResponseSchema[ReleaseRequestOut])
def list_requests(request):
    """
    Returns a list of release requests.
    """

@router.post('/{request_id}/approve', response=ReleaseRequestResult)
def approve_request(request, request_id):
    """
    Approves a request and releases the hold transactionally.
    """

@router.get('/{request_id}/deny', response=ReleaseRequestResult)
def deny_request(request, request_id):
    """
    Denies a release request.
    """