from django.db import models
from django.contrib.postgres.functions import RandomUUID
from django.db.models.functions import Coalesce

from common.enums import DiscountKind, SalesChannel, DiscountStatus
from common.fields import PostgresEnumField
from common.functions import TxNow

class Discount(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    kind = PostgresEnumField('discount_kind', choices=DiscountKind.choices, null=False)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=False)
    channel = PostgresEnumField('sales_channel', db_default=SalesChannel.BOTH, choices=SalesChannel.choices, null=False)
    starts_at = models.DateTimeField(null=False)
    ends_at = models.DateTimeField(null=False)
    min_margin_b2b = models.DecimalField(max_digits=6, decimal_places=4, db_default=0.05, null=False)
    min_margin_b2c = models.DecimalField(max_digits=6, decimal_places=4, db_default=0.10, null=False)
    status = PostgresEnumField('discount_status', db_default=DiscountStatus.SCHEDULED, choices=DiscountStatus.choices, null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)

    # created_by = models.ForeignKey('myadmin.User')

    class Meta:
        db_table = 'discounts'

class DiscountTarget(models.Model):
    # Since composite primary keys don't support generated columns, add a surrogate primary key with a unique
    # constraint for now.
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())

    TARGET_KIND_CHOICES = (
        ('sailing', 'sailing'),
        ('category', 'category'),
        ('cabin', 'cabin'),
    )

    target_kind =  models.TextField(choices=TARGET_KIND_CHOICES, null=False)

    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=False, db_index=False)
    sailing = models.ForeignKey('seasons_sailings.Sailing', on_delete=models.CASCADE, null=True, db_index=False)
    category = models.ForeignKey('catalogs.CabinCategory', on_delete=models.CASCADE, null=True, db_index=False)
    cabin = models.ForeignKey('ships_cabins.Cabin', on_delete=models.CASCADE, null=True, db_index=False)

    # Use a generated column to use in the composite primary key as one of sailing_id, category_id, cabin_id
    # must be non-null, therefore this column will always be non-null and is permitted in a primary key.
    # cabin > category > sailing
    target_id = models.GeneratedField(
        expression=Coalesce(models.F('cabin_id'), models.F('category_id'), models.F('sailing_id')),
        output_field=models.UUIDField(),
        db_persist=True,
        null=False,
    )

    # The below is unsupported by Django 5.2.6, instead enforce uniqueness with a unique constraint.
    # pk = models.CompositePrimaryKey('discount_id', 'target_kind', 'target_id')


    class Meta:
        db_table = 'discount_targets'
        constraints = [
            models.CheckConstraint(
                check=models.Q(target_kind__in=['sailing','category','cabin']),
                name='discount_targets_target_kind_check',
            ),
            models.CheckConstraint(
                check=(
                    (models.Q(target_kind='sailing') &
                     models.Q(sailing__isnull=False, category__isnull=True, cabin__isnull=True)) |
                    (models.Q(target_kind='category') &
                     models.Q(sailing__isnull=True, category__isnull=False, cabin__isnull=True)) |
                    (models.Q(target_kind='cabin') &
                     models.Q(sailing__isnull=True, category__isnull=True, cabin__isnull=False))
                ),
                name='ck_target_exactly_one',
            ),
            models.UniqueConstraint(
                fields=['discount', 'target_kind', 'target_id'],
                name='discount_targets_discount_id_target_kind_target_id_key',
            ),
        ]

