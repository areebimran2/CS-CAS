from django.contrib.postgres.aggregates import JSONBAgg
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
    return ExchangeRatesManual.objects.all()


@router.put('/manual-rates', response=List[ManualFXOut])
def upsert_manual_rates(request, payload: ManualFXInList):
    """
    Upserts (update + insert) a batch of manual rates in one action.
    """
    now = timezone.now()

    pairs = [ExchangeRatesManual(base=pair.base,
                                 quote=pair.quote,
                                 rate=pair.rate,
                                 updated_at=now)
             for pair in payload.rates]

    upsert_pairs = ExchangeRatesManual.objects.bulk_create(
        pairs,
        update_conflicts=True,
        update_fields=['rate', 'updated_at'],
        unique_fields=['base', 'quote']
    )

    return upsert_pairs


@router.get('/manual-rates/{base}/{quote}', response=ManualFXOut)
def get_manual_rate(request, base: Currency, quote: Currency):
    """
    Returns a single manual pair.
    """
    pair = get_object_or_404(ExchangeRatesManual, base=base, quote=quote)
    return pair


@router.get('/live-rates', response=List[LiveFXOut])
def get_live_rates(request, base: Currency, quotes: List[Currency]):
    """
    Returns specific cached live rates for a base currency and a set of quote currencies.
    """




@router.post('/live-rates/refresh', response=List[LiveFXOut])
def refresh_live_rates(request, payload: RefreshLiveFXIn):
    """
    Returns force-refreshed live rates.
    """


@router.get('/status', response=CacheStatusOut)
def get_fx_status(request):
    """
    Returns health/staleness info for the FX provider/cache.
    """
