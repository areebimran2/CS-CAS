from ninja import Router, Path

from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from ships_cabins.schemas import *

router = Router(tags=['D2. Cabin Maps'])


@router.get('', response=NinjaPaginationResponseSchema[CabinMapOut])
@paginate()
def list_cabin_maps(request, ship_id: str = Path(...)):
    """
    Returns a list of the map versions that belong to the specified ship.
    """

@router.get('/{map_id}/zones', response=NinjaPaginationResponseSchema[CabinZoneOut])
@paginate()
def list_cabin_zone(request, map_id, ship_id: str = Path(...)):
    """
    Returns a list of cabin zones belonging to the specified cabin map.
    """

@router.get('/{map_id}', response=CabinMapOut)
def get_cabin_map(request, map_id, ship_id: str = Path(...)):
    """
    Returns a cabin map.
    """

@router.post('', response=CabinMapOut)
def create_cabin_map(request, payload: CabinMapIn, ship_id: str = Path(...)):
    """
    Creates a draft for a new map version.

    Note: version is determined automatically.
    """


@router.post('/{map_id}/upload-url', response=UploadUrlOut)
def cabin_map_upload_url(request, payload: UploadUrlIn, map_id, ship_id: str = Path(...)):
    """
    Returns a presigned upload URL to upload a map asset directly to storage.
    """


@router.put('/{map_id}', response=CabinMapOut)
def update_cabin_map(request, payload: CabinMapUpdateIn, map_id, ship_id: str = Path(...)):
    """
    Update cabin map metadata and/or attach the uploaded asset (returned from the upload URL endpoint) to the map.
    """

@router.put('/{map_id}/zones', response=CabinZoneReplaceOut)
def replace_cabin_zones(request, payload: CabinZoneReplaceIn,  map_id, ship_id: str = Path(...)):
    """
    Saves the map zone geometry -> cabin mapping for the map.

    Note:
    - A "zone" is the selectable region on the map that corresponds to a specific cabin.
    - This is a bulk replace endpoint so it replaces all existing zones for the specified map.
    """


@router.put('/{map_id}/zones/{zone_id}', response=CabinZoneOut)
def update_cabin_zone(request, payload: CabinZoneUpdateIn, map_id, zone_id, ship_id: str = Path(...)):
    """
    Updates one zone from the specified map.
    """


@router.post('/{map_id}/activate', response=CabinMapActivateOut)
def activate_cabin_map(request, map_id, ship_id: str = Path(...)):
    """
    Sets the specified map as the active map version. Demotes previous active to archive.
    """
