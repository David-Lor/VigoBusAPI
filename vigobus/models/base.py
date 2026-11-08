import datetime
import typing

import pydantic


BaseString = typing.Annotated[str, pydantic.constr(strip_whitespace=True)]
NEString = typing.Annotated[str, pydantic.constr(strip_whitespace=True, min_length=1)]
PosInt = typing.Annotated[int, pydantic.conint(gt=0)]
NonNegInt = typing.Annotated[int, pydantic.conint(ge=0)]
NonNegFloat = typing.Annotated[float, pydantic.confloat(ge=0)]


class BaseModel(pydantic.BaseModel):
    class Config:
        validate_assignment = True


class Position(BaseModel):
    lat: float
    lon: float


class SourceMetadata(BaseModel):
    datasource: NEString
    when: datetime.datetime
