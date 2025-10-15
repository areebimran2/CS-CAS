from django.db import models
from django.utils.translation import gettext_lazy as _

# -- User & security
class UserStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Suspended")

# -- Map / Content lifecycle
class MapStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    ARCHIVED = "archived", _("Archived")

# -- Selling life cycles
class HoldStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    RELEASED = "released", _("Released")
    EXPIRED = "expired", _("Expired")
    CONVERTED = "converted", _("Converted")

class BookingStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")

# -- Discounts & channels
class DiscountKind(models.TextChoices):
    PERCENT = "percent", _("Percent")
    FIXED = "fixed", _("Fixed")

class DiscountStatus(models.TextChoices):
    SCHEDULED = "scheduled", _("Scheduled")
    ACTIVE = "active", _("Active")
    ENDED = "ended", _("Ended")
    CANCELLED = "cancelled", _("Cancelled")

class SalesChannel(models.TextChoices):
    B2B = "b2b", _("B2B")
    B2C = "b2c", _("B2C")
    BOTH = "both", _("Both")

# -- Costs & cancellation
class CustomCostMode(models.TextChoices):
    FIXED = "fixed", _("Fixed")
    PERCENT = "percent", _("Percent")

class CustomCostAppliesTo(models.TextChoices):
    PER_CABIN = "per_cabin", _("Per Cabin")
    PER_PAX = "per_pax", _("Per Pax")

class CancellationChargeType(models.TextChoices):
    PERCENT_TOTAL = "percent_total", _("Percent Total")
    PERCENT_COS = "percent_cos", _("Percent COS")
    FIXED_AMOUNT = "fixed_amount", _("Fixed Amount")