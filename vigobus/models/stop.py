import datetime
from typing import Optional

from .base import BaseModel, NEString, PosInt, Position


class StopMetadata(BaseModel):

    class Source(BaseModel):
        datasource: NEString
        when: datetime.datetime

    name_original: NEString
    source: Optional[Source] = None


class Stop(BaseModel):
    id: PosInt
    name: NEString
    position: Optional[Position] = None
    metadata: StopMetadata
