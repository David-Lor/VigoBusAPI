"""GOOGLE MAPS - GETTER MAPS
Functions for acquiring a picture of a Map
"""

# # Native # #
from typing import *

# # Project # #
from vigobusapi.settings import google_maps_settings as settings
from vigobusapi.logger import logger
from ._requester import google_maps_request, ListOfTuples
from ._entities import GoogleMapRequest

__all__ = ("get_map",)

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


async def get_map(request: GoogleMapRequest) -> bytes:
    """Get a static Map picture from the Google Maps Static API. Return the acquired PNG picture as bytes.

    References:
        https://developers.google.com/maps/documentation/maps-static/overview
        https://developers.google.com/maps/documentation/maps-static/start
    """
    logger.bind(map_request=request.dict()).debug("Requesting Google Static Map picture...")
    # TODO cache loaded pictures

    params = _get_map_params(request)
    return (await google_maps_request(url=GOOGLE_MAPS_STATIC_API_URL, params=params)).content
