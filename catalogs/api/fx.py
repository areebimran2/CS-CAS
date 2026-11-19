from typing import List

from django.shortcuts import get_object_or_404
from ninja import Query, Router
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

router = Router(tags=['C4. Exchange Rates'])


@router.get('/manual-rates', response=NinjaPaginationResponseSchema[ManualFXOut])
@requires('fx.view')
@paginate()
def list_manual_rates(request):
    """
    Returns every manual exchange rate (admin maintained), with when it was last updated.
    """
    return ExchangeRatesManual.objects.all()


@router.put('/manual-rates', response=List[ManualFXOut])
@requires('fx.edit')
def upsert_manual_rates(request, payload: ManualFXInList):
    """
    Sets a batch of manual rates in one action: new pairs are added and existing pairs get the new rate.
    """
    return service.upsert_manual_rates(payload.dict()['rates'])


@router.get('/manual-rates/{base}/{quote}', response=ManualFXOut)
@requires('fx.view')
def get_manual_rate(request, base: Currency, quote: Currency):
    """
    Returns one manual rate.
    """
    return get_object_or_404(ExchangeRatesManual, base=base, quote=quote)


@router.delete('/manual-rates/{base}/{quote}', response={204: None})
@requires('fx.edit')
def delete_manual_rate(request, base: Currency, quote: Currency):
    """
    Deletes one manual rate.
    """


@router.get('/live-rates', response=LiveFXOut)
@requires('fx.view')
def get_live_rates(request, base: Currency, quotes: List[Currency] = Query(...)):
    """
    Returns the cached live (XE) rates from `base` to each of `quotes` (repeatable), each with when it was fetched
    and whether it is stale.
    """


@router.post('/live-rates/refresh', response=LiveFXOut)
@requires('fx.edit')
def refresh_live_rates(request, payload: RefreshLiveFXIn):
    """
    Fetches fresh live rates from XE, updates the cache and returns them.
    """


@router.get('/status', response=CacheStatusOut)
@requires('fx.view')
def get_fx_status(request):
    """
    Returns the live rate provider's health: when it was last refreshed and whether its rates are stale.
    """
