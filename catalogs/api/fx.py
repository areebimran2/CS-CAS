from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from pydantic_extra_types.currency_code import Currency

from catalogs.models import ExchangeRatesManual
from catalogs.schemas import (
    CacheStatusOut,
    LiveFXOut,
    ManualFXInList,
    ManualFXOut,
    RefreshLiveFXIn,
)
from catalogs.services import fx as service
from common.access import requires

router = Router(tags=['C4. FX'])


@router.get('/manual-rates', response=NinjaPaginationResponseSchema[ManualFXOut])
@requires('fx.view')
@paginate()
def list_manual_rates(request):
    """
    Returns a list of all stored FX pairs and their rates.
    """
    return ExchangeRatesManual.objects.all()


@router.put('/manual-rates', response=List[ManualFXOut])
@requires('fx.edit')
def upsert_manual_rates(request, payload: ManualFXInList):
    """
    Upserts (update + insert) a batch of manual rates in one action.
    """
    return service.upsert_manual_rates(payload.dict()['rates'])


@router.get('/manual-rates/{base}/{quote}', response=ManualFXOut)
@requires('fx.view')
def get_manual_rate(request, base: Currency, quote: Currency):
    """
    Returns a single manual pair.
    """
    pair = get_object_or_404(ExchangeRatesManual, base=base, quote=quote)
    return pair


@router.get('/live-rates', response=List[LiveFXOut])
@requires('fx.view')
def get_live_rates(request, base: Currency, quotes: List[Currency]):
    """
    Returns specific cached live rates for a base currency and a set of quote currencies.
    """




@router.post('/live-rates/refresh', response=List[LiveFXOut])
@requires('fx.edit')
def refresh_live_rates(request, payload: RefreshLiveFXIn):
    """
    Returns force-refreshed live rates.
    """


@router.get('/status', response=CacheStatusOut)
@requires('fx.view')
def get_fx_status(request):
    """
    Returns health/staleness info for the FX provider/cache.
    """
