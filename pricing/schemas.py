import uuid
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from ninja import Schema, ModelSchema
from ninja_extra.schemas import NinjaPaginationResponseSchema
from pydantic import Field
from pydantic_extra_types.currency_code import Currency

from catalogs.schemas import MoneyOut, Mode, AppliesTo
from ships_cabins.schemas import CabinOut


class FXMode(str, Enum):
    MANUAL = 'manual'
    LIVE = 'live'

class Occupancy(str, Enum):
    DOUBLE = 'double'
    SINGLE = 'single'

class Status(str, Enum):
    PRICED = 'priced'
    UNPRICED = 'unpriced'
    REVIEW = 'review'
    OVERRIDEN = 'overridden'
    ARCHIVED = 'archived'

class EffectiveSource(str, Enum):
    DEFAULT = 'default'
    OVERRIDE = 'override'

class ScopeOut(Schema):
    season: uuid.UUID
    ship: uuid.UUID
    sailings: List[uuid.UUID]
    fx_mode: FXMode
    occupancy: Occupancy

class GraphCoverageOut(Schema):
    cabins_total: int
    priced: int
    unpriced: int
    overriden: int
    archived: int

class GraphCellsOut(Schema):
    sailing: uuid.UUID
    cabin: uuid.UUID
    category: uuid.UUID
    deck: str
    status: Status
    is_overridden: bool
    price_display: MoneyOut

class PricingGraphOut(Schema):
    scope: ScopeOut
    coverage: GraphCoverageOut
    cells: GraphCellsOut

class ListTotalsOut(Schema):
    cos_total: MoneyOut
    b2b_total: MoneyOut
    b2c_total: MoneyOut

class ListItemsOut(Schema):
    sailing: uuid.UUID
    cabin: CabinOut
    status: Status
    effective_source: EffectiveSource
    price_display: MoneyOut
    has_custom_costs: bool

class PricingListOut(Schema):
    scope: ScopeOut
    totals: ListTotalsOut
    page: NinjaPaginationResponseSchema[ListItemsOut]

class BulkTargetIn(Schema):
    category: uuid.UUID

class PricingBulkIn(Schema):
    season: uuid.UUID
    ship: uuid.UUID
    sailings: List[uuid.UUID]

class OverrideIn(Schema):
    base_per_pax: Decimal = Field(max_digits=12, decimal_places=4)
    currency: Currency
    single_multiplier: Decimal = Field("1.50", max_digits=6, decimal_places=4)
    notes: Optional[str] = None

class OverrideCustomCostIn(Schema):
    custom_cost: uuid.UUID
    mode: Mode
    applies_to: AppliesTo
    value: Decimal = Field(max_digits=12, decimal_places=4)
    percent: Optional[Decimal] = Field(max_digits=6, decimal_places=4)
    currency: Currency

class OverrideMarginsIn(Schema):
    b2b: Decimal = Field(max_digits=6, decimal_places=4)
    b2c: Decimal = Field(max_digits=6, decimal_places=4)

class CabinOverrideIn(Schema):
    override: OverrideCustomCostIn
    custom_costs: List[OverrideCustomCostIn]
    margins_override: OverrideMarginsIn