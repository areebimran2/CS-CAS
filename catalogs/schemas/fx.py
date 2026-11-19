from datetime import datetime
from decimal import Decimal
from typing import List

from ninja import ModelSchema, Schema
from pydantic import Field
from pydantic_extra_types.currency_code import Currency

from catalogs.models import ExchangeRatesManual, FXRatesCache
from common.enums import FXProviderStatus


class ManualFXIn(Schema):
    base: Currency
    quote: Currency
    rate: Decimal = Field(gt=0, max_digits=18, decimal_places=8)


class ManualFXOut(ModelSchema):
    class Meta:
        model = ExchangeRatesManual
        fields = '__all__'
        exclude = ['id']


class ManualFXInList(Schema):
    rates: List[ManualFXIn]


class QuoteOut(ModelSchema):
    is_stale: bool

    class Meta:
        model = FXRatesCache
        fields = ['quote', 'rate', 'fetched_at']


class LiveFXOut(ModelSchema):
    quotes: List[QuoteOut]

    class Meta:
        model = FXRatesCache
        fields = ['provider', 'base']


class RefreshLiveFXIn(Schema):
    base: Currency
    quotes: List[Currency] = Field(min_length=1)


class CacheStatusOut(Schema):
    provider: str
    last_refresh_at: datetime
    stale_after_hours: int
    status: FXProviderStatus
