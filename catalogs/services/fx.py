from django.db import transaction
from django.utils import timezone

from catalogs.models import ExchangeRatesManual


@transaction.atomic
def upsert_manual_rates(rates: list[dict]) -> list[ExchangeRatesManual]:
    """Insert each base/quote pair, or update its rate if the pair already exists."""
    now = timezone.now()
    return ExchangeRatesManual.objects.bulk_create(
        [ExchangeRatesManual(base=r['base'], quote=r['quote'], rate=r['rate'], updated_at=now) for r in rates],
        update_conflicts=True, unique_fields=['base', 'quote'], update_fields=['rate', 'updated_at'],
    )
