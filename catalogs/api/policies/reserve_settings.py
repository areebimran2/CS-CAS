from ninja import Router

from catalogs.schemas import *

router = Router(tags=['C5. Reserve Settings'])

@router.get('', response=ReserveSettingsOut)
def get_reserve_settings(request):
    """
    Returns the active global reservation ruleset configuration.
    """

@router.put('', response=ReserveSettingsOut)
def set_reserve_settings(request, payload: ReserveSettingsIn):
    """
    Sets a new active global reservation ruleset configuration.
    """