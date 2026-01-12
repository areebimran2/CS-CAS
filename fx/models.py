from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.functions import TxNow

class ExchangeRatesManual(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    base = models.CharField(max_length=3, null=False)
    quote = models.CharField(max_length=3, null=False)
    rate = models.DecimalField(max_digits=18, decimal_places=8, null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'exchange_rates_manual'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base__regex=r'^[A-Z]{3}$'),
                name='exchange_rates_manual_base_check'
            ),
            models.CheckConstraint(
                condition=models.Q(quote__regex=r'^[A-Z]{3}$'),
                name='exchange_rates_manual_quote_check'
            ),
            models.CheckConstraint(
                condition=models.Q(rate__gt=models.Value(0)),
                name='exchange_rates_manual_rate_check'
            ),
            models.UniqueConstraint(
                fields=['base', 'quote'],
                name='exchange_rates_manual_base_quote_key'
            )
        ]

class FXRatesCache(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    provider = models.TextField(null=False)
    base = models.CharField(max_length=3, null=False)
    quote = models.CharField(max_length=3, null=False)
    rate = models.DecimalField(max_digits=18, decimal_places=8, null=False)
    fetched_at = models.DateTimeField(db_default=TxNow(), null=False)

    class Meta:
        db_table = 'fx_rates_cache'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base__regex=r'^[A-Z]{3}$'),
                name='fx_rates_cache_base_check'
            ),
            models.CheckConstraint(
                condition=models.Q(quote__regex=r'^[A-Z]{3}$'),
                name='fx_rates_cache_quote_check'
            ),
            models.CheckConstraint(
                condition=models.Q(rate__gt=models.Value(0)),
                name='fx_rates_cache_rate_check'
            ),
            models.UniqueConstraint(
                fields=['provider', 'base', 'quote'],
                name='fx_rates_cache_provider_base_quote_key'
            )
        ]
