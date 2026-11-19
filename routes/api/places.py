from ninja import Router

from common.access import requires
from routes.schemas import PlaceDetailsOut, PlacesPredictionsOut
from routes.services.places import places_details_out, places_predictions_out

router = Router(tags=['E2. Places'])


@router.get('/autocomplete', response=PlacesPredictionsOut)
@requires('routes.edit')
async def get_places_autocomplete(request, query: str):
    """
    Suggests ports matching `query`, using Google Places autocomplete.
    """
    return await places_predictions_out(query)


@router.get('/{place_id}', response=PlaceDetailsOut)
@requires('routes.edit')
async def get_place_details(request, place_id: str):
    """
    Returns what a route leg needs for a place chosen from the suggestions: its Place ID, latitude, longitude and
    time zone.
    """
    return await places_details_out(place_id)
