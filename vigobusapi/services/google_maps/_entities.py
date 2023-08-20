"""GOOGLE MAPS - ENTITIES
Classes used to define Google Maps/StreetView API requests
"""

# # Native # #
import string
from enum import Enum
from typing import *

# # Installed # #
from pydantic import BaseModel

# # Project # #
from vigobusapi.utils import ChecksumableClass, new_hash_values, update_hash_values

__all__ = ("GoogleMapRequest", "GoogleStreetviewRequest")


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
        location_x: float
        location_y: float

        @classmethod
        def get_allowed_labels(cls):
            """Get a list with the available labels for Tags, corresponding to numbers 0~9 and characters A~Z."""
            return cls.__ALLOWED_LABELS

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
