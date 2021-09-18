"""GOOGLE MAPS
Functions for getting static Maps and Pictures, using Google Maps and Streetview static APIs
"""

# # Native # #
import string
from enum import Enum
from typing import *

# # Installed # #
import pydantic
from pydantic import BaseModel

# # Project # #
from vigobusapi.settings import google_maps_settings as settings
from vigobusapi.utils import ChecksumableClass, new_hash_values, update_hash_values
from vigobusapi.logger import logger
from .http_requester import http_request, ListOfTuples

__all__ = ("GoogleMapRequest", "GoogleStreetviewRequest", "get_map", "get_photo")

# TODO May refactor in package with different modules (at least split classes and logic)

GOOGLE_MAPS_STATIC_API_URL = "https://maps.googleapis.com/maps/api/staticmap"
GOOGLE_STREETVIEW_STATIC_API_URL = "https://maps.googleapis.com/maps/api/streetview"


def get_labelled_icon_url(label: str) -> str:
    """Get an URL pointing to a picture of a map marker, with a custom label on top of it"""
    # TODO self-hosted generation, and/or cache of generated labels
    return f"https://cdn.mapmarker.io/api/v1/font-awesome/v5/pin?text={label}&size=40&background=D94B43&color=000000&hoffset=-1"


class _GoogleMapsBaseRequest(BaseModel, ChecksumableClass):
    location_x: float
    location_y: float
    size_x: int
    size_y: int

    @property
    def location_str(self) -> Optional[str]:
        if self.location_x is None or self.location_y is None:
            return None
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
        __ALLOWED_LABELS = [*[str(i) for i in range(1, 10)], *[c for c in string.ascii_uppercase]]

        label: Optional[str] = None  # TODO constrain values accepted (avoid enum?)
        icon_url: Optional[str] = None
        location_x: float
        location_y: float

        @classmethod
        def get_allowed_labels(cls):
            return cls.__ALLOWED_LABELS

        @pydantic.root_validator(pre=True)
        def label_to_icon(cls, kwargs: dict):
            """If label is not an "allowed label", generate an icon for it and set it as "icon_url"."""
            label = kwargs.get("label")
            if label not in cls.__ALLOWED_LABELS:
                kwargs["label"] = None
                kwargs["icon_url"] = get_labelled_icon_url(label)
            return kwargs

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

    location_x: Optional[float] = None
    location_y: Optional[float] = None
    tags: Optional[List[Tag]] = None
    zoom: int
    """https://developers.google.com/maps/documentation/maps-static/start#Zoomlevels"""
    map_type: MapTypes


class GoogleStreetviewRequest(_GoogleMapsBaseRequest):
    pass


async def _request(url: str, params: Union[dict, ListOfTuples], expect_http_error: bool = False):
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


def _get_map_tags_params(request_tags: List[GoogleMapRequest.Tag]) -> ListOfTuples:
    params = list()
    for tag in request_tags:
        tag_param_values = [tag.location_str]  # Location always at the end

        if tag.label:
            tag_param_values.insert(0, "label:" + tag.label)
        if tag.icon_url:
            tag_param_values.insert(0, "icon:" + tag.icon_url)

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
    return (await _request(url=GOOGLE_MAPS_STATIC_API_URL, params=params)).content


async def get_photo(request: GoogleStreetviewRequest) -> Optional[bytes]:
    """Get a static StreetView picture from the Google StreetView Static API. Return the acquired PNG picture as bytes.
    If the requested location does not have an available picture, returns None.

    References:
        https://developers.google.com/maps/documentation/streetview/overview
    """
    logger.bind(streetview_request=request.dict()).debug("Requesting Google Static StreetView picture...")
    # TODO cache loaded pictures
    # TODO Support specific parameters for tuning camera, if required
    params = [
        ("location", request.location_str),
        ("size", request.size_str),
        ("return_error_code", "true"),
        ("source", "outdoor")
    ]

    response = await _request(GOOGLE_STREETVIEW_STATIC_API_URL, params=params, expect_http_error=True)
    if response.status_code == 404:
        logger.debug("No StreetView picture available for the request")
        return None

    response.raise_for_status()
    return response.content
