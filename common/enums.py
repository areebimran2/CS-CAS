"""
Every enumeration in the project. Models use them as field choices (the database ones match the PostgreSQL enum types
created in common/migrations/0002), and schemas use them directly as field types.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

# -- User & security

class UserStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Suspended")

class TFAMethod(models.TextChoices):
    SMS = "sms", _("SMS")
    TOTP = "totp", _("TOTP")

class UnAuthPurpose(models.TextChoices):
    """What a one-time passcode is for, before the user is signed in."""
    LOGIN = "login", _("Sign in")

class AuthPurpose(models.TextChoices):
    """What a one-time passcode is for, when a signed-in user changes their security details."""
    VERIFY_OLD_PHONE = "verify-old-phone", _("Verify the current phone number")
    VERIFY_NEW_PHONE = "verify-new-phone", _("Verify the new phone number")
    CHANGE_EMAIL = "change-email", _("Change email")
    CHANGE_PASSWORD = "change-password", _("Change password")
    CHANGE_TFA_METHOD = "change-tfa-method", _("Change the two-factor method")

# -- Map / Content lifecycle

class MapStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    ARCHIVED = "archived", _("Archived")

class MapAssetKind(models.TextChoices):
    SVG = "svg", _("SVG")
    RASTER = "raster", _("Raster image")

# -- Selling life cycles

class HoldStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    RELEASED = "released", _("Released")
    EXPIRED = "expired", _("Expired")
    CONVERTED = "converted", _("Converted")

class BookingStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")

class ReleaseDecision(models.TextChoices):
    APPROVED = "approved", _("Approved")
    DENIED = "denied", _("Denied")

class CabinAvailability(models.TextChoices):
    AVAILABLE = "available", _("Available")
    RESERVED = "reserved", _("Reserved")
    BOOKED = "booked", _("Booked")

class Occupancy(models.TextChoices):
    TWO_PAX = "2-pax", _("2 passengers")
    SINGLE = "single", _("Single")

# -- Discounts & channels

class DiscountKind(models.TextChoices):
    PERCENT = "percent", _("Percent")
    FIXED = "fixed", _("Fixed")

class DiscountStatus(models.TextChoices):
    SCHEDULED = "scheduled", _("Scheduled")
    ACTIVE = "active", _("Active")
    ENDED = "ended", _("Ended")
    CANCELLED = "cancelled", _("Cancelled")

class DiscountTargetKind(models.TextChoices):
    SAILING = "sailing", _("Sailing")
    CATEGORY = "category", _("Category")
    CABIN = "cabin", _("Cabin")

class SalesChannel(models.TextChoices):
    B2B = "b2b", _("B2B")
    B2C = "b2c", _("B2C")
    BOTH = "both", _("Both")

# -- Costs, pricing & cancellation

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

class PricingStatus(models.TextChoices):
    PRICED = "priced", _("Priced")
    UNPRICED = "unpriced", _("Unpriced")
    REVIEW = "review", _("Review")
    OVERRIDDEN = "overridden", _("Overridden")
    ARCHIVED = "archived", _("Archived")

class PriceSource(models.TextChoices):
    BULK = "bulk", _("Bulk (season and ship)")
    OVERRIDE = "override", _("Per-cabin override")

# -- FX

class FXMode(models.TextChoices):
    MANUAL = "manual", _("Manual")
    LIVE = "live", _("Live")

class FXProviderStatus(models.TextChoices):
    OK = "ok", _("OK")
    DEGRADED = "degraded", _("Degraded")
    DOWN = "down", _("Down")

# -- Import, export & reports

class ImportModule(models.TextChoices):
    AMENITIES = "amenities", _("Amenities")
    CABIN_CATEGORIES = "cabin-categories", _("Cabin categories")
    CUSTOM_COSTS = "custom-costs", _("Custom costs")
    SHIPS = "ships", _("Ships")
    CABINS = "cabins", _("Cabins")
    ROUTES = "routes", _("Routes")
    SEASONS = "seasons", _("Seasons")
    SAILINGS = "sailings", _("Sailings")
    PRICING = "pricing", _("Pricing")

class ExportModule(models.TextChoices):
    AMENITIES = "amenities", _("Amenities")
    CABIN_CATEGORIES = "cabin-categories", _("Cabin categories")
    CUSTOM_COSTS = "custom-costs", _("Custom costs")
    SHIPS = "ships", _("Ships")
    CABINS = "cabins", _("Cabins")
    ROUTES = "routes", _("Routes")
    SEASONS = "seasons", _("Seasons")
    SAILINGS = "sailings", _("Sailings")
    PRICING = "pricing", _("List pricing")
    HOLDS = "holds", _("Holds")
    BOOKINGS = "bookings", _("Bookings")
    DISCOUNTS = "discounts", _("Discounts")

class ImportErrorPolicy(models.TextChoices):
    BLOCK_ALL = "block_all", _("Block all rows if any row is invalid")
    SKIP_INVALID = "skip_invalid", _("Import the valid rows, skip the invalid ones")

class FileFormat(models.TextChoices):
    CSV = "csv", _("CSV")
    PDF = "pdf", _("PDF")

class ExportDetail(models.TextChoices):
    SUMMARY = "summary", _("Summary")
    DETAILED = "detailed", _("Detailed")

class Report(models.TextChoices):
    UTILISATION = "utilisation", _("Utilisation")
    PRICING_COVERAGE = "pricing-coverage", _("Pricing coverage")
    HOLDS = "holds", _("Holds and conversions")
    BOOKINGS = "bookings", _("Bookings")
    CANCELLATIONS = "cancellations", _("Cancellations")
    DISCOUNT_UPLIFT = "discount-uplift", _("Discount uplift")
    COS_ROLLUP = "cos-rollup", _("Cost of sale roll-up")
    PICKUP_CURVE = "pickup-curve", _("Pickup curve")

class ReportFrequency(models.TextChoices):
    DAILY = "daily", _("Daily")
    WEEKLY = "weekly", _("Weekly")
    MONTHLY = "monthly", _("Monthly")

# -- Dashboard

class DashboardWidget(models.TextChoices):
    AVAILABLE_CRUISES = "available-cruises", _("Available cruises")
    CRUISE_INVENTORY = "cruise-inventory", _("Cruise inventory")
    TOTAL_COS = "total-cos", _("Total cost of sale")
    ACTIVE_DISCOUNTS = "active-discounts", _("Active discounts")
    NOTIFICATIONS = "notifications", _("Notifications feed")
