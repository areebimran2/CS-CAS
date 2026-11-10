from typing import Optional, List

from ninja import Schema
from pydantic_extra_types.coordinate import Latitude, Longitude


class PlacePrediction(Schema):
    place_id: str
    description: str

class PlacesPredictionsOut(Schema):
    predictions: List[PlacePrediction]

class PlaceDetailsOut(Schema):
    place_id: str
    name: str
    lat: Latitude
    lng: Longitude
    tz: Optional[str] = None
