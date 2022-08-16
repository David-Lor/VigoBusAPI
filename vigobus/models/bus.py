import pydantic

from typing import Optional, List

from .base import BaseModel, NEString, SourceMetadata, NonNegInt, NonNegFloat

__all__ = ("Bus", "BusMetadata", "BusesResponse")


class BusMetadata(BaseModel):
    original_line: NEString
    original_route: NEString
    source: Optional[SourceMetadata] = None


class Bus(BaseModel):
    line: NEString
    route: NEString
    time_minutes: NonNegInt
    distance_meters: Optional[NonNegFloat]
    metadata: BusMetadata


class BusesResponse(BaseModel):
    buses: List[Bus]
    more_buses_available: bool

    @pydantic.validator("buses")
    def _sort_buses(cls, buses: List[Bus]):
        buses.sort(
            key=lambda bus: (
                bus.time_minutes,
                bus.distance_meters or 1000000,
                bus.line,
                bus.route,
            ),
        )
        return buses