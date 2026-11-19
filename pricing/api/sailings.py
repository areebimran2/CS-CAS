import uuid

from ninja import Path, Query, Router

from common.access import requires
from pricing.schemas import CabinOverrideIn, CabinPriceOut, DisplayOptions, SailingMarginsIn, SailingMarginsOut

router = Router(tags=['G2. Sailing Overrides'])


@router.get('/margins', response=SailingMarginsOut)
@requires('pricing.view')
def get_sailing_margins(request, sailing_id: uuid.UUID = Path(...)):
    """
    Returns the B2B and B2C margins in force for the sailing: its override, or else its season's defaults.
    """


@router.put('/margins', response=SailingMarginsOut)
@requires('pricing.override_margin')
def set_sailing_margins(request, payload: SailingMarginsIn, sailing_id: uuid.UUID = Path(...)):
    """
    Overrides the season's default margins for this sailing.
    """


@router.delete('/margins', response=SailingMarginsOut)
@requires('pricing.override_margin')
def reset_sailing_margins(request, sailing_id: uuid.UUID = Path(...)):
    """
    Removes the sailing's margin override, so the season's defaults apply again.
    """


@router.get('/cabins/{cabin_id}', response=CabinPriceOut)
@requires('pricing.view')
def get_cabin_price(request, display: Query[DisplayOptions], cabin_id: uuid.UUID, sailing_id: uuid.UUID = Path(...)):
    """
    The drill-down for one cabin on one sailing: base, custom costs, cost of sale, margins, rack price, discount,
    margin floor and final price for each channel.
    """


@router.put('/cabins/{cabin_id}', response=CabinPriceOut)
@requires('pricing.edit')
def set_cabin_override(request, payload: CabinOverrideIn, cabin_id: uuid.UUID, sailing_id: uuid.UUID = Path(...)):
    """
    Sets a per-cabin price for this sailing, replacing the bulk price. Margins in the override also need the
    `pricing.override_margin` permission.
    """


@router.delete('/cabins/{cabin_id}', response=CabinPriceOut)
@requires('pricing.edit')
def remove_cabin_override(request, cabin_id: uuid.UUID, sailing_id: uuid.UUID = Path(...)):
    """
    Removes the cabin's override, so the bulk price applies again.
    """
