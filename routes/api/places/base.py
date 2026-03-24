from ninja import Router, PatchDict
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from routes.schemas import PlacesPredictionsOut, PlaceDetailsOut
from routes.services.proxy import places_predictions_out, places_details_out

router = Router(tags=['E2. Place'])

@router.get('/autocomplete', response=PlacesPredictionsOut)
async def get_places_autocomplete(request, query: str):
    """
    Returns a "Port (Place Search)" or suggestion list by using a proxy to Google Places autocomplete.
    """
    return await places_predictions_out(query)

@router.get('/{place_id}', response=PlaceDetailsOut)
async def get_places_details(request, place_id):
    """
    Given a place id from the autocomplete suggestion, returns minimal details required for
    route leg (place_id, lat, lng, etc.).
    """
    return await places_details_out(place_id)