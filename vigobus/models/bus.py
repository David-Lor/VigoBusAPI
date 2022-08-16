from typing import Optional, List

from .base import BaseModel, NEString, PosInt, SourceMetadata

__all__ = ("Bus", "BusMetadata", "BusesResponse")


class BusMetadata(BaseModel):
    original_line: NEString
    original_route: NEString
    source: Optional[SourceMetadata] = None


class Bus(BaseModel):
    line: NEString
    route: NEString
    time_minutes: PosInt
    distance_meters: Optional[float]


class BusesResponse(BaseModel):
    buses: List[Bus]
    more_buses_available: bool
