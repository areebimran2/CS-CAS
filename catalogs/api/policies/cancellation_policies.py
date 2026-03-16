from django.shortcuts import get_object_or_404
from ninja import Router

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.schemas.cancellation_policies import (
    CancellationPolicyOut, CancellationPolicyIn, QuoteCancellationChargeIn,
    QuoteCancellationChargeOut,
)
from catalogs.services.cancellation import quote_cancellation_charge as _quote_cancellation_charge
from selling.models import CancellationPolicy, CancellationPolicyTier

router = Router(tags=['C6. Cancellation Policies'])


@router.get('', response=NinjaPaginationResponseSchema[CancellationPolicyOut])
@paginate()
def list_cancellation_policies(request):
    """
    Returns a list of valid cabin cancellation policies available for selection.
    """
    return CancellationPolicy.objects.all()


@router.post('', response=CancellationPolicyOut)
def create_cancellation_policy(request, payload: CancellationPolicyIn):
    """
    Creates a new cabin cancellation policy.
    """
    data = payload.dict(exclude=['tiers'])
    tiers = payload.tiers
    cancellation_policy = CancellationPolicy.objects.create(**data)

    tier_objs = [CancellationPolicyTier(min_days=tier.min_days,
                                        max_days=tier.max_days,
                                        charge_type=tier.charge_type,
                                        value=tier.value,
                                        policy=cancellation_policy)
                 for tier in tiers]

    cancellation_policy.cancellationpolicytier_set.bulk_create(tier_objs)
    cancellation_policy.save()

    return cancellation_policy


@router.get('/{policy_id}', response=CancellationPolicyOut)
def get_cancellation_policy(request, policy_id):
    """
    Returns a cabin cancellation policy.
    """
    cancellation_policy = get_object_or_404(CancellationPolicy, id=policy_id)


    return cancellation_policy


@router.put('/{policy_id}', response=CancellationPolicyOut)
def replace_cancellation_policy(request, payload: CancellationPolicyIn, policy_id):
    """
    Replaces a cabin cancellation policy and its tiers.
    """
    data = payload.dict(exclude=['tiers'])
    cancellation_policy = get_object_or_404(CancellationPolicy, id=policy_id)

    cancellation_policy.cancellationpolicytier_set.all().delete()

    tiers = payload.tiers
    tier_objs = [CancellationPolicyTier(min_days=tier.min_days,
                                        max_days=tier.max_days,
                                        charge_type=tier.charge_type,
                                        value=tier.value,
                                        policy=cancellation_policy)
                 for tier in tiers]

    for attr, value in data.items():
        setattr(cancellation_policy, attr, value)

    cancellation_policy.cancellationpolicytier_set.bulk_create(tier_objs)

    cancellation_policy.save()
    return cancellation_policy

@router.post('/{policy_id}/quote', response=QuoteCancellationChargeOut)
def quote_cancellation_charge(request, payload: QuoteCancellationChargeIn, policy_id):
    """
    Runs the cancellation tier engine using some cancellation policy to return an estimated charge and the tier that
    would apply (pre-booking).
    """
    return _quote_cancellation_charge(policy_id, payload.departure_date, payload.today, payload.total, payload.cos)
