from ninja import Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from catalogs.schemas import *

router = Router(tags=['C4. FX'])

@router.get('/manual-rates', response=NinjaPaginationResponseSchema[ManualFXOut])
@paginate()
def list_manual_rates(request):
    """
    Returns a list of all stored FX pairs and their rates.
    """

@router.put('/manual-rates', response=List[ManualFXOut])
def upsert_manual_rates(request, payload: ManualFXInList):
    """
    Upserts (update + insert) a batch of manual rates in one action.
    """

@router.get('/manual-rates/{base}/{quote}', response=ManualFXOut)
def get_manual_rate(request, base: str, quote: str):
    """
    Returns a single manual pair.
    """

@router.get('/live-rates', response=List[LiveFXOut])
def get_live_rates(request, base: str, quote: str):
    """
    Returns a specific cached live rates for a base currency and a set of quote currencies.
    """

@router.get('/live-rates/refresh', response=List[LiveFXOut])
def refresh_live_rates(request, payload: RefreshLiveFXIn):
    """
    Returns force-refreshed live rates.
    """

@router.get('/status', response=CacheStatusOut)
def get_fx_status(request):
    """
    Returns health/staleness info for the FX provider/cache.
    """
