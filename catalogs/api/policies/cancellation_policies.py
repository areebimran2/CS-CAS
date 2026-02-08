from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.schemas import CancellationPolicyOut, CancellationPolicyIn, QuoteCancellationChargeIn, \
    QuoteCancellationChargeOut

router = Router(tags=['C6. Cancellation Policies'])

@router.get('', response=NinjaPaginationResponseSchema[CancellationPolicyOut])
@paginate()
def list_cancellation_policies(request):
    """
    Returns a list of valid cabin cancellation policies available for selection.
    """

@router.post('', response=CancellationPolicyOut)
def create_cancellation_policy(request, payload: CancellationPolicyIn):
    """
    Creates a new cabin cancellation policy.
    """

@router.get('/{policy_id}', response=CancellationPolicyOut)
def get_cancellation_policy(request, policy_id):
    """
    Returns a cabin cancellation policy.
    """

@router.put('/{policy_id}', response=CancellationPolicyOut)
def replace_cancellation_policy(request, payload: CancellationPolicyIn, policy_id):
    """
    Replaces a cabin cancellation policy and its tiers.
    """

@router.post('/{policy_id}/quote', response=QuoteCancellationChargeOut)
def quote_cancellation_charge(request, payload: QuoteCancellationChargeIn, policy_id):
    """
    Runs the cancellation tier engine using some cancellation policy to return an estimated charge and the tier that
    would apply (pre-booking).
    """