"""GOOGLE MAPS
Functions for getting static Maps and Pictures, using Google Maps and Streetview static APIs
"""

# # Native # #
from enum import Enum
from typing import *

# # Installed # #
from pydantic import BaseModel

# # Project # #
from vigobusapi.settings import google_maps_settings as settings
from vigobusapi.utils import ChecksumableClass, new_hash_values, update_hash_values
from vigobusapi.logger import logger
from .http_requester import http_request, ListOfTuples

__all__ = ("GoogleMapRequest", "get_map")

# TODO May refactor in package with different modules (at least split classes and logic)

GOOGLE_MAPS_STATIC_API_URL = "https://maps.googleapis.com/maps/api/staticmap"


class _GoogleMapsBaseRequest(BaseModel, ChecksumableClass):
    location_x: float
    location_y: float
    size_x: int
    size_y: int

    @property
    def location_str(self):
        return f"{self.location_x},{self.location_y}"

    @property
    def size_str(self):
        return f"{self.size_x}x{self.size_y}"

    @property
    def checksum_hash(self):
        """Returns a SHA256 checksum of all the fields in the request"""
        return new_hash_values(
            self.location_x,
            self.location_y,
            self.size_x,
            self.size_y,
            algorithm="sha256"
        )


class GoogleMapRequest(_GoogleMapsBaseRequest):

    # Embed classes #

    class Tag(BaseModel, ChecksumableClass):
        label: Optional[str]  # single uppercase char (A~Z, 0~9)
        location_x: float
        location_y: float

        @property
        def location_str(self):
            return f"{self.location_x},{self.location_y}"

        @property
        def checksum_hash(self):
            return new_hash_values(
                self.label,
                self.location_x,
                self.location_y,
                algorithm="md5"
            )

    class MapTypes(str, Enum):
        """Available map types.

        References:
            https://developers.google.com/maps/documentation/maps-static/start#MapTypes
        """
        roadmap = "roadmap"
        """specifies a standard roadmap image, as is normally shown on the Google Maps website"""
        satellite = "satellite"
        """specifies a satellite image"""
        terrain = "terrain"
        """specifies a physical relief map image, showing terrain and vegetation"""
        hybrid = "hybrid"
        """specifies a hybrid of the satellite and roadmap image,
        showing a transparent layer of major streets and place names on the satellite image"""

    # Properties #

    @property
    def checksum_hash(self):
        _hash = super().checksum_hash

        if self.tags:
            sorted_tags_checksums = sorted(tag.checksum_value for tag in self.tags)
        else:
            sorted_tags_checksums = "NoTags"

        return update_hash_values(
            self.zoom,
            self.map_type.value,
            sorted_tags_checksums,
            _hash=_hash
        )

    # Class Attributes #

    tags: Optional[List[Tag]] = None
    zoom: int  # TODO may be used by Streetview as well (refactor if so)
    """https://developers.google.com/maps/documentation/maps-static/start#Zoomlevels"""
    map_type: MapTypes


async def _request(url: str, params: Union[dict, ListOfTuples]):
    """HTTP requester for Google Maps API calls, automatically including the configured API key.
    Raises exception if the API Key is not configured.

    :param url: URL for the Google API, WITHOUT query parameters
    :param params: query parameters
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
        retries=1
    )


async def get_map(request: GoogleMapRequest) -> bytes:
    """Get a static Map picture from the Google Maps Static API. Return the acquired picture as bytes.

    References:
        https://developers.google.com/maps/documentation/maps-static/overview
        https://developers.google.com/maps/documentation/maps-static/start
    """
    logger.bind(map_request=request.dict()).debug("Requesting Google Static Map picture...")
    # TODO cache loaded pictures
    params = [
        ("center", request.location_str),
        ("size", request.size_str),
        ("zoom", str(request.zoom)),
        ("maptype", request.map_type.value)
    ]

    if request.tags:
        for tag in request.tags:
            tag_param_values = [tag.location_str]  # Location always at the end

            if tag.label:
                tag_param_values.insert(0, "label:" + tag.label)

            tag_param = "|".join(tag_param_values)
            params.append(("markers", tag_param))

    return (await _request(url=GOOGLE_MAPS_STATIC_API_URL, params=params)).content
