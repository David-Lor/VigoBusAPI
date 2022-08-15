from typing import Optional

from .base import BaseModel, NEString, PosInt


class Bus(BaseModel):
    line: NEString
    route: NEString
    time_minutes: PosInt
    distance_meters: Optional[float]
