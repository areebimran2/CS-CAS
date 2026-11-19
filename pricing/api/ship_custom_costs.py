import uuid

from ninja import Path, Router

from common.access import requires
from pricing.schemas import ShipCustomCostsIn, ShipCustomCostsOut

router = Router(tags=['G3. Ship Custom Costs'])


@router.get('', response=ShipCustomCostsOut)
@requires('pricing.view')
def get_ship_custom_costs(request, ship_id: uuid.UUID = Path(...)):
    """
    Returns the custom costs (port fees and so on) that can be applied to the ship's cabins.
    """


@router.put('', response=ShipCustomCostsOut)
@requires('pricing.edit')
def replace_ship_custom_costs(request, payload: ShipCustomCostsIn, ship_id: uuid.UUID = Path(...)):
    """
    Replaces the custom costs that can be applied to the ship's cabins. Costs already used in its pricing stay.
    """
