import math

from django.shortcuts import get_object_or_404

from catalogs.schemas.cancellation_policies import ChargeType
from selling.models import CancellationPolicy, CancellationPolicyTier


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

