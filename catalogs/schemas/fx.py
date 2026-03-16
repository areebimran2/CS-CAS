from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import List

from ninja import Schema, ModelSchema
from pydantic_extra_types.currency_code import Currency

from fx.models import ExchangeRatesManual, FXRatesCache

from pydantic import Field


class Status(str, Enum):
    OK = 'ok'
    DEGRADED = 'degraded'
    DOWN = 'down'


class ManualFXIn(Schema):
    base: Currency
    quote: Currency
    rate: Decimal = Field(max_digits=18, decimal_places=8)


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
        fields = ['rate', 'fetched_at']


class LiveFXOut(ModelSchema):
    quotes: List[QuoteOut]

    class Meta:
        model = FXRatesCache
        fields = ['provider', 'base']


class RefreshLiveFXIn(Schema):
    base: str
    quotes: List[str]


class CacheStatusOut(Schema):
    provider: str
    last_refresh_at: datetime
    stale_after_hours: int
    status: Status

