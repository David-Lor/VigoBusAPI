from typing import Optional

from .base import BaseModel, NEString, PosInt, Position, SourceMetadata

__all__ = ("StopMetadata", "Stop")


class StopMetadata(BaseModel):
    original_name: NEString
    source: Optional[SourceMetadata] = None


class Stop(BaseModel):
    id: PosInt
    name: NEString
    position: Optional[Position] = None
    metadata: StopMetadata
