from ninja import Router

from common.access import requires
from catalogs.models import ReserveSetting
from catalogs.schemas import ReserveSettingsIn, ReserveSettingsOut

router = Router(tags=['C5. Reserve Settings'])

@router.get('', response=ReserveSettingsOut)
@requires('policies.view')
def get_reserve_settings(request):
    """
    Returns the active global reservation ruleset configuration.
    """
    settings = ReserveSetting.objects.order_by('-created_at').first()
    return settings


@router.put('', response=ReserveSettingsOut)
@requires('policies.edit')
def set_reserve_settings(request, payload: ReserveSettingsIn):
    """
    Sets a new active global reservation ruleset configuration.
    """
    settings = ReserveSetting.objects.order_by('-created_at').first()

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(settings, attr, value)

    settings.save()
    return settings