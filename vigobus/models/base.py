import datetime

import pydantic


class BaseString(pydantic.ConstrainedStr):
    strip_whitespace = True


class NEString(BaseString):
    min_length = 1


class PosInt(pydantic.ConstrainedInt):
    gt = 0


class NonNegInt(pydantic.ConstrainedInt):
    ge = 0


class NonNegFloat(pydantic.ConstrainedFloat):
    ge = 0


class BaseModel(pydantic.BaseModel):
    class Config:
        validate_assignment = True


class Position(pydantic.BaseModel):
    lat: float
    lon: float


class SourceMetadata(BaseModel):
    datasource: NEString
    when: datetime.datetime
