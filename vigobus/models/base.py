import datetime

import pydantic


class BaseString(pydantic.ConstrainedStr, str):
    strip_whitespace = True


class NEString(BaseString):
    min_length = 1


class PosInt(pydantic.ConstrainedInt, int):
    gt = 0


class NonNegInt(pydantic.ConstrainedInt, int):
    ge = 0


class NonNegFloat(pydantic.ConstrainedFloat, float):
    ge = 0


class BaseModel(pydantic.BaseModel):
    class Config:
        validate_assignment = True


class Position(BaseModel):
    lat: float
    lon: float


class SourceMetadata(BaseModel):
    datasource: NEString
    when: datetime.datetime
