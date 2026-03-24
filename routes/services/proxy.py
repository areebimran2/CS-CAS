import httpx

PLACES_BASE = 'https://places.googleapis.com/v1/places'

async def places_predictions_out(query: str):
    """
    Fetches a "Port (Place Search)" or suggestion list by calling the Google Places API.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f'{PLACES_BASE}:autocomplete', params={
            'input': query
        }, headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': 'AIzaSyDPsTakZqZIero3W2_K39WckigJva6cnPA'
        })
        response.raise_for_status()
        data = response.json()

        places = []

        for suggestion in data.get('suggestions', []):
            prediction = suggestion['placePrediction']
            places.append({
                'place_id': prediction['placeId'],
                'description': prediction['text']['text'],
            })

        return {
            'predictions': places,
        }

async def places_details_out(place_id: str):
    """
    Fetches the place details for a selected Google Place ID. Used after autocomplete to populate leg fields
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{PLACES_BASE}/{place_id}', headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': 'AIzaSyDPsTakZqZIero3W2_K39WckigJva6cnPA',
            'X-Goog-FieldMask': 'id,displayName,location,timeZone'
        })
        response.raise_for_status()
        data = response.json()

        return {
            'place_id': data['id'],
            'name': data['displayName']['text'],
            'lat': data['location']['latitude'],
            'lng': data['location']['longitude'],
            'tz': data['timeZone']['id']
        }