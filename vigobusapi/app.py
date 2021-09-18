"""APP
Module with all the available endpoints and the FastAPI initialization.
"""

# # Native # #
import io
import json
from typing import Optional, Set

# # Installed # #
import uvicorn
from fastapi import FastAPI, Response, Query, Depends, HTTPException
from starlette.responses import StreamingResponse

# # Project # #
from vigobusapi.entities import Stop, Stops, BusesResponse
from vigobusapi.request_handler import request_handler
from vigobusapi.settings import settings, google_maps_settings
from vigobusapi.vigobus_getters import get_stop, get_stops, get_buses, search_stops
from vigobusapi.services.google_maps import GoogleMapRequest, GoogleStreetviewRequest, get_map, get_photo
from vigobusapi.services import MongoDB
from vigobusapi.logger import logger

__all__ = ("app", "run")

app = FastAPI(
    title=settings.api_name
)
app.middleware("http")(request_handler)


@app.on_event("startup")
async def app_setup():
    """This function runs when FastAPI starts, before accepting requests."""
    # Initialize MongoDB
    await MongoDB.initialize()


@app.get("/status")
async def endpoint_status():
    return Response(
        content="OK",
        media_type="text/plain",
        status_code=200
    )


@app.get("/stops", response_model=Stops)
async def endpoint_get_stops(
        stop_name: Optional[str] = Query(None),
        limit: Optional[int] = Query(None),
        stops_ids: Optional[Set[int]] = Query(None, alias="stop_id")
):
    """Endpoint to search/list stops by different filters. Only one filter can be used.
    Returns 400 if no filters given.
    The filters available are:

    - stop_name: search by a single string in stop names. "limit" can be used for limiting results size.
    - stop_id: repeatable param for getting multiple stops by id on a single request. Not found errors are ignored.
    """
    with logger.contextualize(**locals()):
        if stop_name is not None:
            stops = await search_stops(stop_name=stop_name, limit=limit)
        elif stops_ids:
            stops = await get_stops(stops_ids)
        else:
            raise HTTPException(status_code=400, detail="No filters given")
        return [stop.dict() for stop in stops]


@app.get("/stop/{stop_id}", response_model=Stop)
async def endpoint_get_stop(stop_id: int):
    """Endpoint to get information of a Stop giving the Stop ID
    """
    with logger.contextualize(**locals()):
        stop = await get_stop(stop_id)
        return stop.dict()


@app.get("/buses/{stop_id}", response_model=BusesResponse)
@app.get("/stop/{stop_id}/buses", response_model=BusesResponse)
async def endpoint_get_buses(stop_id: int, get_all_buses: bool = False):
    """Endpoint to get a list of Buses coming to a Stop giving the Stop ID.
    By default the shortest available list of buses is returned, unless 'get_all_buses' param is True
    """
    with logger.contextualize(**locals()):
        buses_result = await get_buses(stop_id, get_all_buses=get_all_buses)
        return buses_result.dict()


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


@app.get("/stop/{stop_id}/map")
async def endpoint_get_stop_map(
        stop_id: int,
        map_params: MapQueryParams = Depends()
):
    """Get a picture of a map with the stop location marked on it."""
    stop = await get_stop(stop_id)
    if (stop.lat, stop.lon) == (None, None):
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


@app.get("/stops/map")
async def endpoint_get_stops_map(
        stops_ids: Set[int] = Query(None, alias="stop_id", min_items=1, max_items=35),
        map_params: MapQueryParams = Depends(),
):
    """Get a picture of a map with the locations of the given stops marked on it.
    The marks are labelled in the same order as the given stops ids.

    A header "X-Stops-Tags" is returned, being a JSON associating the Stops IDs with the tag label on the map,
    with the format: {"<stop id>" : "<tag label>"}
    """
    stops = await get_stops(stops_ids)

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


@app.get("/stop/{stop_id}/photo")
async def endpoint_get_stop_photo(
        stop_id: int,
        size_x: int = google_maps_settings.stop_photo_default_size_x,
        size_y: int = google_maps_settings.stop_photo_default_size_y,
):
    stop = await get_stop(stop_id)
    if (stop.lat, stop.lon) == (None, None):
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


def run():
    """Run the API using Uvicorn
    """
    logger.info("Running the app with uvicorn")

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level
    )


if __name__ == '__main__':
    run()
