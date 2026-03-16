from ninja import Router

from selling.models import ReserveSetting
from catalogs.schemas import ReserveSettingsIn, ReserveSettingsOut

router = Router(tags=['C5. Reserve Settings'])

@router.get('', response=ReserveSettingsOut)
def get_reserve_settings(request):
    """
    Returns the active global reservation ruleset configuration.
    """
    settings = ReserveSetting.objects.order_by('-created_at').first()
    return settings


@router.put('', response=ReserveSettingsOut)
def set_reserve_settings(request, payload: ReserveSettingsIn):
    """
    Sets a new active global reservation ruleset configuration.
    """
    settings = ReserveSetting.objects.order_by('-created_at').first()

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(settings, attr, value)

    settings.save()
    return settings