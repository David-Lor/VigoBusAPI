import random
from typing import Optional, List

import httpx
import pydantic

from vigobus.models import BusesResponse, Stop
from vigobus.exceptions import DatasourceMethodUnavailableException
from vigobus.models.base import NonNegInt
from vigobus.models.request import HttpSettings

__all__ = ("BaseDatasource",)


class BaseDatasource(pydantic.BaseModel):
    # TODO Docstring

    http_settings: HttpSettings = pydantic.Field(default_factory=HttpSettings)

    getbuses_notallbuses_limit: Optional[NonNegInt] = None
    """For the `get_buses` method, if get_all_buses=False and the datasource returns all the buses available,
    shorten the results to this amount, if not None.
    """

    async def get_all_stops(self) -> List[Stop]:
        """Get all the available stops, typically as a static dump.

        :return: AsyncIterable of Stop objects
        """
        raise self._get_unavailable_exception()

    async def get_all_stops_etag(self) -> str:
        """Get the cache key for the get_all_stops method. This can be used for determining whether the get_all_stops
        dump has changed in the datasource.

        :return: an arbitrary identifier as string.
        """
        raise self._get_unavailable_exception()

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        """Search for a Stop by id.
        The datasource should either return the data of the Stop, or be sure that the Stop does not exist in reality.

        :param stop_id: id of the Stop to get.
        :return: Stop object if stop found; None if the stop does not exist.
        """
        raise self._get_unavailable_exception()

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        """Get the buses arriving to the given Stop, with their remaining time estimations, by Stop id.

        :param stop_id: id of the Stop to search Buses on.
        :param get_all_buses: if True, fetch all the available buses.
            This is used by datasources that paginate the list of buses.
        :return: BusesResponse object with the list of buses fetched.
        :raises StopNotExistException: when the Stop requested does not exist.
        :raises DatasourceMethodUnavailableException: when the method is not implemented for the datasource.
        """
        raise self._get_unavailable_exception()

    async def _request_http(self, url: str, raise_status: bool = True, **kwargs) -> httpx.Response:
        """Simple HTTP requester, supporting retries."""

        # TODO review retries system. Include retries_delay_seconds
        retries = self.http_settings.retries

        # noinspection inconsistent-returns
        for i in range(retries):
            async with httpx.AsyncClient(timeout=self.http_settings.request_timeout_seconds, proxy=self._get_proxy()) as client:
                client: httpx.AsyncClient
                kwargs.setdefault("method", "GET")
                try:
                    r = await client.request(
                        url=url,
                        **kwargs,
                    )
                    if raise_status:
                        r.raise_for_status()
                    return r

                except httpx.RequestError as ex:
                    if i + 1 >= retries:
                        raise ex

        raise httpx.HTTPError("No successful request could be made after {} retries.".format(retries))

    def _get_proxy(self):
        if not (proxy_settings := self.http_settings.proxy):
            return None

        return random.choice(proxy_settings.urls)

    @property
    def datasource_name(self):
        return self.get_datasource_name()

    @classmethod
    def get_datasource_name(cls):
        return cls.__name__

    @classmethod
    def _get_unavailable_exception(cls):
        return DatasourceMethodUnavailableException(getter_name=cls.get_datasource_name())
