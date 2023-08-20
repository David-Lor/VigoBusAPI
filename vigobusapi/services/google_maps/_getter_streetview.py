"""GOOGLE MAPS - GETTER STREETVIEW
Functions for acquiring a photo of a location
"""

# # Native # #
import asyncio
from typing import *

# # Project # #
from vigobusapi.logger import logger
from ._entities import GoogleStreetviewRequest
from ._requester import google_maps_request, ListOfTuples
from ._cache import save_cached_metadata, get_cached_metadata, CachedMap

__all__ = ("get_photo",)

GOOGLE_MAPS_STATIC_API_URL = "https://maps.googleapis.com/maps/api/staticmap"
GOOGLE_STREETVIEW_STATIC_API_URL = "https://maps.googleapis.com/maps/api/streetview"


def _get_photo_params(request: GoogleStreetviewRequest) -> ListOfTuples:
    params = [
        ("location", request.location_str),
        ("size", request.size_str),
        ("return_error_code", "true"),
        ("source", "outdoor")
    ]
    return params


async def get_photo_from_api(request: GoogleStreetviewRequest) -> Tuple[Optional[bytes], Optional[CachedMap]]:
    """Get a static StreetView picture from the Google StreetView Static API.
    Return the acquired PNG picture as bytes, and the CachedMap object.
    If the requested location does not have an available picture, returns None.
    The fetched picture is persisted on cache, running a fire & forget background task.

    References:
        https://developers.google.com/maps/documentation/streetview/overview
    """
    logger.bind(streetview_request=request.dict()).debug("Requesting Google Static StreetView picture...")
    # TODO Support specific parameters for tuning camera, if required

    params = _get_photo_params(request)
    response = await google_maps_request(GOOGLE_STREETVIEW_STATIC_API_URL, params=params, expect_http_error=True)
    if response.status_code == 404:
        logger.debug("No StreetView picture available for the request")
        return None, None

    response.raise_for_status()
    image = response.content
    logger.debug("Photo acquired from Google StreetView Static API")

    cache_metadata = await save_cached_metadata(request=request, image=image, background=True)
    return image, cache_metadata


async def get_photo(
        request: GoogleStreetviewRequest, read_cache_first: bool = True
) -> Tuple[Optional[bytes], Optional[CachedMap]]:
    """Get a static StreetView picture from cache (if read_cache_first=True) or the Google StreetView Static API.
    Return the acquired PNG picture as bytes, and the CachedMap object.
    If the requested location does not have an available picture, returns (None, None)."""
    if read_cache_first:
        cached_metadata = await get_cached_metadata(request, fetch_image=True)
        if cached_metadata:
            return cached_metadata.image, cached_metadata

    return await get_photo_from_api(request)
