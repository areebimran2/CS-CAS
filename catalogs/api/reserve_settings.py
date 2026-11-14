from ninja import Router

from catalogs.schemas import ReserveSettingsIn, ReserveSettingsOut
from catalogs.services import reserve_settings as service
from common.access import requires

router = Router(tags=['C5. Reserve Settings'])


@router.get('', response=ReserveSettingsOut)
@requires('policies.view')
def get_reserve_settings(request):
    """
    Returns the active global reservation ruleset configuration.
    """
    return service.current_reserve_settings()


@router.put('', response=ReserveSettingsOut)
@requires('policies.edit')
def set_reserve_settings(request, payload: ReserveSettingsIn):
    """
    Sets a new active global reservation ruleset configuration.
    """
    return service.update_reserve_settings(payload.dict(exclude_unset=True))
