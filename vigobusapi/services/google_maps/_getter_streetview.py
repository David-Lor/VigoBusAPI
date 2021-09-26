"""GOOGLE MAPS - GETTER STREETVIEW
Functions for acquiring a photo of a location
"""

# # Native # #
from typing import *

# # Project # #
from vigobusapi.logger import logger
from ._entities import GoogleStreetviewRequest
from ._requester import google_maps_request, ListOfTuples

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


async def get_photo(request: GoogleStreetviewRequest) -> Optional[bytes]:
    """Get a static StreetView picture from the Google StreetView Static API. Return the acquired PNG picture as bytes.
    If the requested location does not have an available picture, returns None.

    References:
        https://developers.google.com/maps/documentation/streetview/overview
    """
    logger.bind(streetview_request=request.dict()).debug("Requesting Google Static StreetView picture...")
    # TODO cache loaded pictures
    # TODO Support specific parameters for tuning camera, if required

    params = _get_photo_params(request)
    response = await google_maps_request(GOOGLE_STREETVIEW_STATIC_API_URL, params=params, expect_http_error=True)
    if response.status_code == 404:
        logger.debug("No StreetView picture available for the request")
        return None

    response.raise_for_status()
    return response.content
