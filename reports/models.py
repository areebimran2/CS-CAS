from django.db import models
from django.contrib.postgres.functions import RandomUUID

from common.functions import TxNow

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    entity = models.TextField(null=False)  # -- e.g., 'pricing', 'discount'
    entity_id = models.UUIDField(null=True)
    action = models.TextField(null=False)  # -- e.g., 'create','update','archive','override'
    before = models.JSONField(null=True)
    after = models.JSONField(null=True)
    ts = models.DateTimeField(db_default=TxNow(), null=False)

    # actor = models.ForeignKey('myadmin.User', on_delete=models.SET_NULL, null=True, db_index=False)

    class Meta:
        db_table = 'audit_log'
        indexes = [
            models.Index(fields=['entity', 'entity_id'], name='idx_audit_entity'),
        ]

# -- Example fact table (optional; populated by jobs)
# class FactUtilization(models.Model):
#     day = models.DateField(null=False)
#     cabins_total = models.IntegerField(null=False)
#     cabins_sold = models.IntegerField(null=False)
#     cabins_held = models.IntegerField(null=False)
#
#     ship = models.ForeignKey('ships_cabins.Ship', on_delete=models.RESTRICT, null=False, db_index=False)
#     sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.RESTRICT, null=False, db_index=False)
#
#     pk = models.CompositePrimaryKey('day', 'ship_id', 'sailing_id')
#
#     class Meta:
#         db_table = 'fact_utilization'


# -- Materialized views (define and refresh in jobs)
# -- CREATE MATERIALIZED VIEW mv_pricing_coverage AS ...
# -- CREATE MATERIALIZED VIEW mv_pickup_curve     AS ...