"""ENTITIES
Classes and data models used along the project
"""

# # Native # #
import datetime
import hashlib
from typing import Optional, Union, List

# # Installed # #
import pydantic

# # Package # #
from vigobusapi.exceptions import StopNotExist

__all__ = ("BaseMongoModel", "Stop", "Stops", "OptionalStop", "StopOrNotExist", "Bus", "Buses", "BusesResponse")


class BaseModel(pydantic.BaseModel):
    def dict(self, *args, skip_none=True, **kwargs):
        # if kwargs.get("skip_defaults") is None:
        #     kwargs["skip_defaults"] = True
        d = super().dict(*args, **kwargs)
        return {k: v for k, v in d.items() if (not skip_none or v is not None)}


class BaseMongoModel(pydantic.BaseModel):
    # TODO Use in Stop models
    class Config(pydantic.BaseModel.Config):
        id_field: Optional[str] = None

    def to_mongo(self, **kwargs) -> dict:
        d = self.dict(**kwargs)
        if self.Config.id_field is None:
            return d

        d["_id"] = d.pop(self.Config.id_field)
        return d

    @classmethod
    def from_mongo(cls, d: dict):
        if cls.Config.id_field is not None:
            d[cls.Config.id_field] = d.pop("_id")

        # noinspection PyArgumentList
        return cls(**d)


class Bus(BaseModel):
    line: str
    route: str
    time: int
    bus_id: str = None

    @pydantic.root_validator(pre=True)
    def _generate_bus_id(cls, data):
        if not data.get("bus_id"):
            md5 = hashlib.md5()
            md5.update(data["line"].encode())
            md5.update(data["route"].encode())
            bus_id = md5.hexdigest()
            return {**data, "bus_id": bus_id}
        return data


class BusesResponse(BaseModel):
    buses: List[Bus]
    more_buses_available: bool
    source: Optional[str]


class Stop(BaseModel):
    stop_id: int
    name: str
    lat: Optional[float]
    lon: Optional[float]
    original_name: Optional[str]
    source: Optional[str]
    created: Optional[datetime.datetime]

    def __init__(self, **kwargs):
        # From Mongo to Python
        # Translate _id to stop_id
        try:
            kwargs["stop_id"] = kwargs.pop("_id")
        except KeyError:
            # Raise the exception on the super entity Init (stop_id is always required)
            pass
        super().__init__(**kwargs)

    def get_mongo_dict(self):
        """Call this method instead of dict() to save the stop in MongoDB
        """
        # From Python to Mongo
        # Translate stop_id to _id
        d = self.dict()
        d["_id"] = d.pop("stop_id")
        # Remove source field
        d.pop("source")
        return d

    @property
    def has_location(self):
        return self.lat is not None and self.lon is not None


OptionalStop = Optional[Stop]
StopOrNotExist = Union[Stop, StopNotExist]
Stops = List[Stop]
Buses = List[Bus]
