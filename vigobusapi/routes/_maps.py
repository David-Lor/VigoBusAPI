"""MAPS Routes
"""

# # Native # #
import io
import json
from dataclasses import dataclass
from typing import *

# # Installed # #
from fastapi import APIRouter, Query, Depends, HTTPException, Response
from starlette.responses import StreamingResponse, PlainTextResponse

# # Project # #
from vigobusapi.settings import google_maps_settings
from vigobusapi.vigobus_getters import get_stop, get_stops
from vigobusapi.services.google_maps import (GoogleMapRequest, GoogleStreetviewRequest,
                                             get_map, get_photo, get_cached_metadata, update_cached_metadata, CachedMap)

__all__ = ("router",)

router = APIRouter()


@dataclass
class MapQueryParams:
    size_x: int = google_maps_settings.stop_map_default_size_x
    size_y: int = google_maps_settings.stop_map_default_size_y
    zoom: int = google_maps_settings.stop_map_default_zoom
    map_type: GoogleMapRequest.MapTypes = google_maps_settings.stop_map_default_type


@dataclass
class PhotoQueryParams:
    size_x: int = google_maps_settings.stop_photo_default_size_x
    size_y: int = google_maps_settings.stop_photo_default_size_y


@dataclass
class MapCacheSetParams:
    id: str
    telegram_file_id: str


StopsTagsRelation = Dict[int, GoogleMapRequest.Tag]


def _format_map_response(
        image: Optional[bytes] = None,
        telegram_file_id: Optional[str] = None,
        cache_metadata: Optional[CachedMap] = None,
        stops_tags_relation: Optional[StopsTagsRelation] = None
) -> Response:
    """Generate a Response for a fetched image or cached item, based on the given arguments."""
    headers = dict()
    if cache_metadata is not None:
        headers["X-Maps-Cache-ID"] = cache_metadata.id
    if stops_tags_relation is not None:
        headers["X-Maps-Stops-Tags"] = json.dumps(stops_tags_relation)

    if image is not None:
        return StreamingResponse(content=io.BytesIO(image), media_type="image/png", headers=headers)
    if telegram_file_id is not None:
        return PlainTextResponse(content=telegram_file_id, headers=headers)
    raise Exception("No file data or cache given for generating Response")


@router.get("/stop/{stop_id}/map")
@router.get("/stops/{stop_id}/map")
async def endpoint_get_stop_map(
        stop_id: int,
        map_params: MapQueryParams = Depends(),
        get_telegram_file_id: bool = False
):
    """Get a picture of a map with the stop location marked on it.

    If get_telegram_file_id=True, fetch the cached Telegram File ID and return it as plaintext.
    If not available, the picture (cached or live) is returned.

    A header "X-Maps-Cache-ID" is returned, with the Cache ID of the map with the queried parameters.
    This can be used for updating the cache.
    """
    stop = await get_stop(stop_id)
    if not stop.has_location:
        raise HTTPException(status_code=409, detail="The stop does not have information about the location")

    map_request = GoogleMapRequest(
        location_x=stop.lat,
        location_y=stop.lon,
        size_x=map_params.size_x,
        size_y=map_params.size_y,
        zoom=map_params.zoom,
        map_type=map_params.map_type,
        tags=[GoogleMapRequest.Tag(location_x=stop.lat, location_y=stop.lon)]
    )

    if get_telegram_file_id:
        cache_metadata = await get_cached_metadata(map_request, fetch_image=False)
        if cache_metadata and cache_metadata.telegram_file_id:
            return _format_map_response(
                telegram_file_id=cache_metadata.telegram_file_id, cache_metadata=cache_metadata
            )

    image, cache_metadata = await get_map(map_request)
    return _format_map_response(image=image, cache_metadata=cache_metadata)


@router.get("/stops/map")
async def endpoint_get_stops_map(
        stops_ids: Set[int] = Query(None, alias="stop_id",
                                    min_items=1, max_items=len(GoogleMapRequest.Tag.get_allowed_labels())),
        map_params: MapQueryParams = Depends(),
        get_telegram_file_id: bool = False
):
    """Get a picture of a map with the locations of the given stops marked on it.

    If get_telegram_file_id=True, fetch the cached Telegram File ID and return it as plaintext.
    If not available, the picture (cached or live) is returned.

    Non existing stops, or those without location available, are ignored,
    but if none of the given stops are valid, returns 404.

    A header "X-Maps-Stops-Tags" is returned, being a JSON associating the Stops IDs with the tag label on the map,
    with the format: {"<stop id>" : "<tag label>"}

    A header "X-Maps-Cache-ID" is returned, with the Cache ID of the map with the queried parameters.
    This can be used for updating the cache.
    """
    stops = await get_stops(stops_ids)
    stops = [stop for stop in stops if stop.has_location]
    if not stops:
        raise HTTPException(status_code=404, detail="None of the stops exist or have location available")

    stops_tags: List[GoogleMapRequest.Tag] = list()
    stops_tags_relation: StopsTagsRelation = dict()
    for i, stop in enumerate(stops):
        tag_label = GoogleMapRequest.Tag.get_allowed_labels()[i]
        tag = GoogleMapRequest.Tag(label=tag_label, location_x=stop.lat, location_y=stop.lon)
        stops_tags.append(tag)
        stops_tags_relation[stop.stop_id] = tag_label

    map_request = GoogleMapRequest(
        size_x=map_params.size_x,
        size_y=map_params.size_y,
        zoom=map_params.zoom,
        map_type=map_params.map_type,
        tags=stops_tags
    )

    if get_telegram_file_id:
        cache_metadata = await get_cached_metadata(map_request, fetch_image=False)
        if cache_metadata and cache_metadata.telegram_file_id:
            return _format_map_response(
                telegram_file_id=cache_metadata.telegram_file_id,
                cache_metadata=cache_metadata,
                stops_tags_relation=stops_tags_relation
            )

    image, cache_metadata = await get_map(map_request)
    return _format_map_response(image=image, cache_metadata=cache_metadata, stops_tags_relation=stops_tags_relation)


@router.get("/stop/{stop_id}/photo")
@router.get("/stops/{stop_id}/photo")
async def endpoint_get_stop_photo(
        stop_id: int,
        photo_params: PhotoQueryParams = Depends(),
        get_telegram_file_id: bool = False
):
    """Get a real street photo of the Stop location.

    If get_telegram_file_id=True, fetch the cached Telegram File ID and return it as plaintext.
    If not available, the picture (cached or live) is returned.

    A header "X-Maps-Cache-ID" is returned, with the Cache ID of the map with the queried parameters.
    This can be used for updating the cache.
    """
    stop = await get_stop(stop_id)
    if not stop.has_location:
        raise HTTPException(status_code=409, detail="The stop does not have information about the location")

    photo_request = GoogleStreetviewRequest(
        location_x=stop.lat,
        location_y=stop.lon,
        size_x=photo_params.size_x,
        size_y=photo_params.size_y
    )

    if get_telegram_file_id:
        cache_metadata = await get_cached_metadata(photo_request, fetch_image=False)
        if cache_metadata and cache_metadata.telegram_file_id:
            return _format_map_response(telegram_file_id=cache_metadata.telegram_file_id, cache_metadata=cache_metadata)

    image, cache_metadata = await get_photo(photo_request)
    if not image:
        raise HTTPException(status_code=404, detail="No StreetView photo available for the stop location")
    return _format_map_response(image=image, cache_metadata=cache_metadata)


@router.put("/cache/maps", status_code=204)
async def update_maps_cache(cache_params: MapCacheSetParams = Depends()):
    """Update fields from a cached map or photo. Can be used for setting the Telegram File ID of a persisted photo."""
    updated = await update_cached_metadata(cache_id=cache_params.id, telegram_file_id=cache_params.telegram_file_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"No cache found with id {cache_params.id}")
    return Response(status_code=204)
