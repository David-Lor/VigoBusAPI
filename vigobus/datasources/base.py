import httpx
import pydantic

from typing import Optional, List

from ..models import BusesResponse, Stop
from ..exceptions import DatasourceMethodUnavailableException
from ..models.base import PosInt, NonNegFloat, NonNegInt

__all__ = ("BaseDatasource",)


class BaseDatasource(pydantic.BaseModel):
    # TODO Docstring

    http_retries: PosInt = 3
    http_retries_delay_seconds: NonNegFloat = 1
    http_request_timeout_seconds: NonNegFloat = 5
    buses_per_page: Optional[NonNegInt] = None

    async def get_all_stops(self) -> List[Stop]:
        """Get all the available stops.

        :return: List of Stop objects.
        """
        raise DatasourceMethodUnavailableException

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        """Search for a Stop by id.
        The datasource should either return the data of the Stop, or be sure that the Stop does not exist in reality.

        :param stop_id: id of the Stop to get.
        :return: Stop object if stop found; None if the stop does not exist.
        """
        raise DatasourceMethodUnavailableException

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        """Get the buses arriving to the given Stop, with their remaining time estimations, by Stop id.

        :param stop_id: id of the Stop to search Buses on.
        :param get_all_buses: if True, fetch all the available buses.
            This is used by datasources that paginate the list of buses.
        :return: BusesResponse object with the list of buses fetched.
        :raises StopNotExistException: when the Stop requested does not exist.
        :raises DatasourceMethodUnavailableException: when the method is not implemented for the datasource.
        """
        raise DatasourceMethodUnavailableException

    async def _request_http(self, url: str, raise_status: bool = True, **kwargs) -> httpx.Response:
        """Simple HTTP requester, supporting retries."""
        async with httpx.AsyncClient(timeout=self.http_request_timeout_seconds) as client:
            client: httpx.AsyncClient
            kwargs.setdefault("method", "GET")

            for i in range(self.http_retries):
                try:
                    r = await client.request(
                        url=url,
                        **kwargs,
                    )
                    if raise_status:
                        r.raise_for_status()
                    return r
                except httpx.RequestError as ex:
                    if i + 1 >= self.http_retries:
                        raise ex

    @property
    def datasource_name(self):
        return self.__class__.__name__
