import datetime

import pydantic


class BaseString(pydantic.ConstrainedStr):
    strip_whitespace = True


class NEString(BaseString):
    min_length = 1


class PosInt(pydantic.ConstrainedInt):
    gt = 0


class BaseModel(pydantic.BaseModel):
    pass


class Position(pydantic.BaseModel):
    lat: float
    lon: float


class SourceMetadata(BaseModel):
    datasource: NEString
    when: datetime.datetime
