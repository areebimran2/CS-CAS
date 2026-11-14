from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.models import CancellationPolicy
from catalogs.schemas.cancellation_policies import (
    CancellationPolicyIn,
    CancellationPolicyOut,
    QuoteCancellationChargeIn,
    QuoteCancellationChargeOut,
)
from catalogs.services import cancellation_policies as service
from common.access import requires

router = Router(tags=['C6. Cancellation Policies'])


@router.get('', response=NinjaPaginationResponseSchema[CancellationPolicyOut])
@requires('policies.view')
@paginate()
def list_cancellation_policies(request):
    """
    Returns a list of valid cabin cancellation policies available for selection.
    """
    return CancellationPolicy.objects.all()


@router.post('', response=CancellationPolicyOut)
@requires('policies.create')
def create_cancellation_policy(request, payload: CancellationPolicyIn):
    """
    Creates a new cabin cancellation policy.
    """
    return service.create_cancellation_policy(**payload.dict())


@router.get('/{policy_id}', response=CancellationPolicyOut)
@requires('policies.view')
def get_cancellation_policy(request, policy_id):
    """
    Returns a cabin cancellation policy.
    """
    return get_object_or_404(CancellationPolicy, id=policy_id)


@router.put('/{policy_id}', response=CancellationPolicyOut)
@requires('policies.edit')
def replace_cancellation_policy(request, payload: CancellationPolicyIn, policy_id):
    """
    Replaces a cabin cancellation policy and its tiers.
    """
    policy = get_object_or_404(CancellationPolicy, id=policy_id)
    return service.replace_cancellation_policy(policy, **payload.dict())


@router.post('/{policy_id}/quote', response=QuoteCancellationChargeOut)
@requires('policies.view')
def quote_cancellation_charge(request, payload: QuoteCancellationChargeIn, policy_id):
    """
    Runs the cancellation tier engine using some cancellation policy to return an estimated charge and the tier that
    would apply (pre-booking).
    """
    return service.quote_cancellation_charge(policy_id, payload.departure_date, payload.today, payload.total,
                                             payload.cos)
