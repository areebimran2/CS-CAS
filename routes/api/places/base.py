from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from routes.schemas import *

router = Router(tags=['E2. Places'])

@router.get('/autocomplete', response=PlaceOut)
def get_places_autocomplete(request):
    """
    Returns a "Port (Place Search)" or suggestion list by using a proxy to Google Places autocomplete.
    """

@router.get('/details', response=PlaceDetailsOut)
def get_places_details(request, place_id):
    """
    Given a place id from the autocomplete suggestion, returns minimal details required for
    route leg (place_id, lat, lng, etc.).
    """