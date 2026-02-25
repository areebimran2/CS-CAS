from ninja import Router

from catalogs.schemas import *

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
    active_settings = ReserveSetting.objects.order_by('-created_at').first()

    for attr, value in payload.items():
        setattr(active_settings, attr, value)

    active_settings.save()
    return active_settings