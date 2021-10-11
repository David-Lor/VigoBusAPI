"""MAPS Routes
"""

# # Native # #
import io
import json
from typing import Set

# # Installed # #
from fastapi import APIRouter, Query, Depends, HTTPException
from starlette.responses import StreamingResponse

# # Project # #
from vigobusapi.settings import google_maps_settings
from vigobusapi.vigobus_getters import get_stop, get_stops
from vigobusapi.services.google_maps import GoogleMapRequest, GoogleStreetviewRequest, get_map, get_photo

__all__ = ("router",)

router = APIRouter()


class MapQueryParams:
    def __init__(
            self,
            size_x: int = google_maps_settings.stop_map_default_size_x,
            size_y: int = google_maps_settings.stop_map_default_size_y,
            zoom: int = google_maps_settings.stop_map_default_zoom,
            map_type: GoogleMapRequest.MapTypes = google_maps_settings.stop_map_default_type
    ):
        self.size_x = size_x
        self.size_y = size_y
        self.zoom = zoom
        self.map_type = map_type


@router.get("/stop/{stop_id}/map")
@router.get("/stops/{stop_id}/map")
async def endpoint_get_stop_map(
        stop_id: int,
        map_params: MapQueryParams = Depends()
):
    """Get a picture of a map with the stop location marked on it."""
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
    map_data = await get_map(map_request)
    return StreamingResponse(io.BytesIO(map_data), media_type="image/png")


@router.get("/stops/map")
async def endpoint_get_stops_map(
        stops_ids: Set[int] = Query(None, alias="stop_id",
                                    min_items=1, max_items=len(GoogleMapRequest.Tag.get_allowed_labels())),
        map_params: MapQueryParams = Depends(),
):
    """Get a picture of a map with the locations of the given stops marked on it.

    Non existing stops, or those without location available, are ignored,
    but if none of the given stops are valid, returns 404.

    A header "X-Stops-Tags" is returned, being a JSON associating the Stops IDs with the tag label on the map,
    with the format: {"<stop id>" : "<tag label>"}
    """
    stops = await get_stops(stops_ids)
    stops = [stop for stop in stops if stop.has_location]
    if not stops:
        raise HTTPException(status_code=404, detail="None of the stops exist or have location available")

    stops_tags = list()
    stops_tags_relation = dict()
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
    map_data = await get_map(map_request)

    return StreamingResponse(
        content=io.BytesIO(map_data),
        media_type="image/png",
        headers={"X-Stops-Tags": json.dumps(stops_tags_relation)}
    )


@router.get("/stop/{stop_id}/photo")
@router.get("/stops/{stop_id}/photo")
async def endpoint_get_stop_photo(
        stop_id: int,
        size_x: int = google_maps_settings.stop_photo_default_size_x,
        size_y: int = google_maps_settings.stop_photo_default_size_y,
):
    stop = await get_stop(stop_id)
    if not stop.has_location:
        raise HTTPException(status_code=409, detail="The stop does not have information about the location")

    photo_request = GoogleStreetviewRequest(
        location_x=stop.lat,
        location_y=stop.lon,
        size_x=size_x,
        size_y=size_y
    )
    photo_data = await get_photo(photo_request)
    if not photo_data:
        raise HTTPException(status_code=404, detail="No StreetView photo available for the stop location")
    return StreamingResponse(io.BytesIO(photo_data), media_type="image/png")
