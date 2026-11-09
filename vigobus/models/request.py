import pydantic
from .base import PosInt, NonNegFloat


class HttpSettings(pydantic.BaseModel):

    class ProxySettings(pydantic.BaseModel):
        urls: list[str]

    retries: PosInt = 3
    retries_delay_seconds: NonNegFloat = 1
    request_timeout_seconds: NonNegFloat = 5

    proxy: ProxySettings | None = None
