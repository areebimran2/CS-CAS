import math

from django.db import transaction
from django.shortcuts import get_object_or_404

from catalogs.models import CancellationPolicy, CancellationPolicyTier
from common.enums import CancellationChargeType as ChargeType
from common.services import update_instance


@transaction.atomic
def create_cancellation_policy(*, tiers: list[dict], **fields) -> CancellationPolicy:
    policy = CancellationPolicy.objects.create(**fields)
    _create_tiers(policy, tiers)
    return policy


@transaction.atomic
def replace_cancellation_policy(policy: CancellationPolicy, *, tiers: list[dict], **fields) -> CancellationPolicy:
    """Replace the policy's fields and all of its tiers. If any tier is invalid, nothing changes."""
    policy.cancellationpolicytier_set.all().delete()
    _create_tiers(policy, tiers)
    return update_instance(policy, fields)


def _create_tiers(policy, tiers):
    CancellationPolicyTier.objects.bulk_create([CancellationPolicyTier(policy=policy, **tier) for tier in tiers])


def quote_cancellation_charge(policy_id, departure_date, today, total, cos):
    """
    Runs the cancellation tier engine using some cancellation policy to return an estimated charge and the tier that
    would apply (pre-booking).

    :param policy_id: The cancellation policy ID
    :param departure_date: The departure date
    :param today: Today's date (as provided by the client)
    :param total: MoneyOut-like object with .amount and .currency
    :param cos: MoneyOut-like object with .amount and .currency
    :return: dict with days_out, tier, and charge
    """
    cancellation_policy = get_object_or_404(CancellationPolicy, id=policy_id)

    days_out = math.ceil((departure_date - today).days)

    tier = CancellationPolicyTier.objects.filter(
        policy=cancellation_policy,
        min_days__lte=days_out,
        max_days__gte=days_out
    ).order_by('-min_days').first()

    # Assuming tier exists
    if tier.charge_type == ChargeType.PERCENT_TOTAL:
        charge = total.amount * tier.value
    elif tier.charge_type == ChargeType.PERCENT_COS:
        charge = cos.amount * tier.value
    else:
        # Fixed amount
        charge = tier.value

    clamped = max(0, min(charge, total.amount))

    return {
        'days_out': days_out,
        'tier': tier,
        'charge': {
            'amount': clamped,
            'currency': total.currency
        }
    }

