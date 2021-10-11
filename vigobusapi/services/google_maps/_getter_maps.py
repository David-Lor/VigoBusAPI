"""GOOGLE MAPS - GETTER MAPS
Functions for acquiring a picture of a Map
"""

# # Native # #
import asyncio
from typing import *

# # Project # #
from vigobusapi.settings import google_maps_settings as settings
from vigobusapi.logger import logger
from ._requester import google_maps_request, ListOfTuples
from ._entities import GoogleMapRequest
from ._cache import save_cached_metadata, get_cached_metadata

__all__ = ("get_map", "get_map_from_api")

GOOGLE_MAPS_STATIC_API_URL = "https://maps.googleapis.com/maps/api/staticmap"


def _get_map_tags_params(request_tags: List[GoogleMapRequest.Tag]) -> ListOfTuples:
    params = list()
    for tag in request_tags:
        tag_param_values = [tag.location_str]  # Location always at the end

        if tag.label:
            tag_param_values.insert(0, "label:" + tag.label)

        tag_param = "|".join(tag_param_values)
        params.append(("markers", tag_param))

    return params


def _get_map_params(request: GoogleMapRequest) -> ListOfTuples:
    params = [
        ("size", request.size_str),
        ("maptype", request.map_type.value),
        ("language", settings.language),
        ("format", "png8"),
    ]

    location_str = request.location_str
    if location_str:
        params.append(("center", location_str))
        params.append(("zoom", str(request.zoom)))

    if request.tags:
        params.extend(_get_map_tags_params(request.tags))

    return params


async def get_map_from_api(request: GoogleMapRequest) -> bytes:
    """Get a static Map picture from the Google Maps Static API. Return the acquired PNG picture as bytes.
    The fetched picture is persisted on cache, running a fire & forget background task.

    References:
        https://developers.google.com/maps/documentation/maps-static/overview
        https://developers.google.com/maps/documentation/maps-static/start
    """
    logger.bind(map_request=request.dict()).debug("Requesting Google Static Map picture...")
    params = _get_map_params(request)

    image = (await google_maps_request(url=GOOGLE_MAPS_STATIC_API_URL, params=params)).content
    logger.debug("Map acquired from Google Static Maps API")

    asyncio.create_task(save_cached_metadata(request=request, image=image))
    return image


async def get_map(request: GoogleMapRequest, read_cache_first: bool = True) -> bytes:
    """Get a static Map picture from cache (if read_cache_first=True) or the Google Maps Static API.
    Return the acquired PNG picture as bytes."""
    image = None

    if read_cache_first:
        cached_metadata = await get_cached_metadata(request, fetch_image=True)
        if cached_metadata:
            image = cached_metadata.image

    if image is None:
        image = await get_map_from_api(request)

    return image
