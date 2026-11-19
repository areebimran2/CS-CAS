import uuid
from typing import List

from ninja import Schema

from catalogs.schemas import CustomCostOut


class ShipCustomCostsIn(Schema):
    """The custom costs that can be applied to the ship's cabins (spec: "link cost applicability to ship")."""
    custom_cost_ids: List[uuid.UUID]


class ShipCustomCostsOut(Schema):
    ship_id: uuid.UUID
    custom_costs: List[CustomCostOut]
