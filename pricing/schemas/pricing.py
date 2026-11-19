"""Schemas shared by the pricing views (G1), per-sailing overrides (G2) and list pricing (H1)."""
import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated, List, Optional

from ninja import Schema
from pydantic import Field, model_validator
from pydantic_extra_types.currency_code import Currency

from common.enums import FXMode, Occupancy, PriceSource, PricingStatus
from common.exceptions import ValidationFailedError
from common.schemas import Money, OptionalStr
from ships_cabins.schemas import CabinOut

Multiplier = Annotated[Decimal, Field(ge=1, max_digits=6, decimal_places=4, description='Single occupancy; 1.50 = +50%')]
Margin = Annotated[Decimal, Field(ge=0, max_digits=6, decimal_places=4, description='0.15 means 15%')]


# -- Shared inputs

class DisplayOptions(Schema):
    """How prices are shown. Conversion is for display only; stored prices keep their currency."""
    fx_mode: FXMode = FXMode.MANUAL
    occupancy: Occupancy = Occupancy.TWO_PAX
    display_currency: Optional[Currency] = Field(default=None, description='Defaults to each price\'s own currency')


class PricingScope(DisplayOptions):
    """The season, ship and sailings a pricing screen covers (spec G1)."""
    season_id: uuid.UUID
    ship_id: uuid.UUID
    sailing_id: List[uuid.UUID] = Field(default=[], description='Repeatable. Empty means every sailing in scope')


class CustomCostValueIn(Schema):
    """A custom cost's value for the cabins it's applied to. Fixed costs give `value`, percent costs `percent`."""
    custom_cost_id: uuid.UUID
    value: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=4)
    percent: Optional[Decimal] = Field(default=None, ge=0, max_digits=6, decimal_places=4, description='0..1')
    currency: Optional[Currency] = None

    @model_validator(mode='after')
    def exactly_one_of_value_or_percent(self):
        if (self.value is None) == (self.percent is None):
            raise ValidationFailedError(errors=[{'field': 'value', 'message': 'Give either value or percent'}])
        return self


# -- Shared outputs

class PriceTotalsOut(Schema):
    cos: Money
    sales_b2b: Money
    sales_b2c: Money


class CustomCostLineOut(Schema):
    custom_cost_id: uuid.UUID
    label: str
    amount: Money


class AppliedDiscountOut(Schema):
    discount_id: uuid.UUID
    name: str
    floor_applied: bool = Field(description='The margin floor stopped the full discount being applied')


class ChannelPriceOut(Schema):
    margin: Decimal
    rack: Money
    discount: Optional[AppliedDiscountOut]
    final: Money


class CabinPriceOut(Schema):
    """One cabin's price on one sailing, step by step (spec "pricing order of operations")."""
    sailing_id: uuid.UUID
    cabin: CabinOut
    status: PricingStatus
    source: Optional[PriceSource] = Field(description='None when the cabin is unpriced')
    base_per_pax: Optional[Money]
    single_multiplier: Optional[Decimal]
    custom_costs: List[CustomCostLineOut]
    cos: Optional[Money]
    b2b: Optional[ChannelPriceOut]
    b2c: Optional[ChannelPriceOut]
    notes: Optional[str] = None


# -- G1. Graph, lines and bulk

class CoverageOut(Schema):
    cabins_total: int
    priced: int
    unpriced: int
    review: int
    overridden: int
    archived: int


class GraphCellOut(Schema):
    sailing_id: uuid.UUID
    cabin_id: uuid.UUID
    category_id: uuid.UUID
    deck: Optional[str]
    status: PricingStatus
    price: Optional[Money] = Field(description='Final B2C price in the display currency; None when unpriced')


class PricingGraphOut(Schema):
    coverage: CoverageOut
    cells: List[GraphCellOut]


class PricingLinesOut(Schema):
    totals: PriceTotalsOut
    lines: List[CabinPriceOut]


class BulkTargetIn(Schema):
    """Which of the ship's current cabins to price. Given filters combine; none means every cabin."""
    category_ids: Optional[List[uuid.UUID]] = None
    decks: Optional[List[str]] = None
    cabin_ids: Optional[List[uuid.UUID]] = None


class PricingBulkIn(Schema):
    season_id: uuid.UUID
    ship_id: uuid.UUID
    sailing_ids: List[uuid.UUID] = Field(min_length=1)
    target: BulkTargetIn = BulkTargetIn()
    base_per_pax: Decimal = Field(ge=0, max_digits=12, decimal_places=4)
    currency: Currency
    single_multiplier: Multiplier = Decimal('1.50')
    custom_costs: List[CustomCostValueIn] = []


class PricingBulkOut(Schema):
    cabins_priced: int
    sailings: int


# -- G2. Per-sailing overrides

class SailingMarginsIn(Schema):
    """Margins for one sailing, replacing the season's defaults. Needs the `pricing.override_margin` permission."""
    margin_b2b: Margin
    margin_b2c: Margin


class SailingMarginsOut(Schema):
    sailing_id: uuid.UUID
    margin_b2b: Decimal
    margin_b2c: Decimal
    overridden: bool = Field(description='False when these are the season\'s defaults')


class CabinOverrideIn(Schema):
    """A per-cabin price for one sailing, replacing the bulk price (spec G3)."""
    base_per_pax: Decimal = Field(ge=0, max_digits=12, decimal_places=4)
    currency: Currency
    single_multiplier: Multiplier = Decimal('1.50')
    custom_costs: List[CustomCostValueIn] = []
    margin_b2b: Optional[Margin] = Field(default=None, description='Needs `pricing.override_margin`')
    margin_b2c: Optional[Margin] = Field(default=None, description='Needs `pricing.override_margin`')
    notes: OptionalStr = None


# -- H1. List pricing

class ListPricingFilter(DisplayOptions):
    season_id: Optional[uuid.UUID] = None
    ship_id: Optional[List[uuid.UUID]] = None
    departure_from: Optional[date] = None
    departure_to: Optional[date] = None
    nights: Optional[int] = None
    route_id: Optional[uuid.UUID] = None
    category_id: Optional[List[uuid.UUID]] = None
    deck: Optional[str] = None
    status: Optional[List[PricingStatus]] = None
    search: Optional[str] = None


class SailingTotalsOut(Schema):
    sailing_id: uuid.UUID
    departure_date: date
    nights: int
    totals: PriceTotalsOut
    coverage: CoverageOut


class ShipTotalsOut(Schema):
    ship_id: uuid.UUID
    name: str
    totals: PriceTotalsOut
    sailings: List[SailingTotalsOut]


class SeasonTotalsOut(Schema):
    season_id: uuid.UUID
    name: str
    totals: PriceTotalsOut
    ships: List[ShipTotalsOut]


class ListPricingOut(Schema):
    """Totals grouped season → ship → sailing, with overall totals (spec H)."""
    totals: PriceTotalsOut
    seasons: List[SeasonTotalsOut]
