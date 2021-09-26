"""GOOGLE MAPS - REQUESTER
Functions for requesting the Google Maps/StreetView APIs
"""

# # Native # #
from typing import *

# # Project # #
from vigobusapi.settings import google_maps_settings as settings
from vigobusapi.services.http_requester import http_request, ListOfTuples

__all__ = ("google_maps_request", "ListOfTuples")


async def google_maps_request(url: str, params: Union[dict, ListOfTuples], expect_http_error: bool = False):
    """HTTP requester for Google Maps API calls, automatically including the configured API key.
    Raises exception if the API Key is not configured.

    :param url: URL for the Google API, WITHOUT query parameters
    :param params: query parameters
    :param expect_http_error: if True, raise_for_status=False and not_retry_400_errors=True
    """
    if not settings.enabled:
        raise Exception("Google Maps API Key not set in settings")

    if isinstance(params, list):
        params.append(("key", settings.api_key))
    else:
        params = dict(**params, key=settings.api_key)

    return await http_request(
        url=url,
        method="GET",
        params=params,
        retries=1,
        raise_for_status=not expect_http_error,
        not_retry_400_errors=expect_http_error
    )
