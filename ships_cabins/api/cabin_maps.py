import uuid

from ninja import Path, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from ships_cabins.schemas import (
    CabinMapActivateOut,
    CabinMapIn,
    CabinMapOut,
    CabinMapUpdateIn,
    CabinZoneOut,
    CabinZoneReplaceIn,
    CabinZoneReplaceOut,
    CabinZoneUpdateIn,
    DetectedZoneOut,
    UploadUrlIn,
    UploadUrlOut,
)

router = Router(tags=['D2. Cabin Maps'])


@router.get('', response=NinjaPaginationResponseSchema[CabinMapOut])
@requires('ships.view')
@paginate()
def list_cabin_maps(request, ship_id: uuid.UUID = Path(...)):
    """
    Returns the ship's cabin map versions, newest first.
    """


@router.post('', response=CabinMapOut)
@requires('ships.create')
def create_cabin_map(request, payload: CabinMapIn, ship_id: uuid.UUID = Path(...)):
    """
    Creates a draft for the ship's next map version. The version number is assigned automatically.
    """


@router.get('/active', response=CabinMapOut)
@requires('ships.view')
def get_active_cabin_map(request, ship_id: uuid.UUID = Path(...)):
    """
    Returns the ship's active map with its zones: the deck plan staff click to select a cabin. 404 if no map is active.
    """


@router.get('/{map_id}', response=CabinMapOut)
@requires('ships.view')
def get_cabin_map(request, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Returns a map version with its zones, e.g. to preview a draft before activating it.
    """


@router.put('/{map_id}', response=CabinMapOut)
@requires('ships.edit')
def update_cabin_map(request, payload: CabinMapUpdateIn, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Updates a draft map's notes and attaches its uploaded asset (from the upload URL endpoint).
    """


@router.delete('/{map_id}', response={204: None})
@requires('ships.delete')
def delete_cabin_map(request, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Deletes a draft map. Active and archived maps are kept as history, so they respond 409.
    """


@router.post('/{map_id}/upload-url', response=UploadUrlOut)
@requires('ships.edit')
def create_cabin_map_upload_url(request, payload: UploadUrlIn, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Returns a presigned URL to upload the map's SVG, JPG or PNG directly to storage.
    """


@router.post('/{map_id}/auto-detect', response=list[DetectedZoneOut])
@requires('ships.edit')
def auto_detect_cabin_zones(request, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Finds the cabin regions in the map's SVG and suggests the cabin for each, matching labels to cabin numbers.
    Nothing is saved: review the suggestions, then save them with `PUT .../zones`.
    """


@router.post('/{map_id}/activate', response=CabinMapActivateOut)
@requires('ships.edit')
def activate_cabin_map(request, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Makes this map the ship's active map. The previously active map, if any, is archived.
    """


@router.post('/{map_id}/archive', response=CabinMapOut)
@requires('ships.edit')
def archive_cabin_map(request, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Archives a map version. Archiving the active map leaves the ship without one.
    """


# -- Zones: the clickable region of the map for each cabin

@router.get('/{map_id}/zones', response=NinjaPaginationResponseSchema[CabinZoneOut])
@requires('ships.view')
@paginate()
def list_cabin_zones(request, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Returns the map's zones, each linked to a cabin.
    """


@router.put('/{map_id}/zones', response=CabinZoneReplaceOut)
@requires('ships.edit')
def replace_cabin_zones(request, payload: CabinZoneReplaceIn, map_id: uuid.UUID, ship_id: uuid.UUID = Path(...)):
    """
    Replaces all of the map's zones. A cabin can appear only once per map.
    """


@router.put('/{map_id}/zones/{zone_id}', response=CabinZoneOut)
@requires('ships.edit')
def update_cabin_zone(request, payload: CabinZoneUpdateIn, map_id: uuid.UUID, zone_id: uuid.UUID,
                      ship_id: uuid.UUID = Path(...)):
    """
    Updates one zone's shape or the cabin it links to.
    """
