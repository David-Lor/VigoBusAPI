import httpx
import pydantic

from typing import Optional, Type, Dict, List

from ..models import BusesResponse, Stop
from ..exceptions import DatasourceMethodUnavailableException
from ..models.base import PosInt, NonNegFloat

__all__ = ("BaseDatasource", "Datasources")


class BaseDatasource(pydantic.BaseModel):
    # TODO Docstring

    http_retries: PosInt = 3
    http_retries_delay_seconds: NonNegFloat = 1
    http_request_timeout_seconds: NonNegFloat = 5

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


class Datasources:
    # TODO Docstring

    _datasources: Dict[Type[BaseDatasource], int] = dict()
    _datasources_sorted: List[Type[BaseDatasource]] = list()

    @classmethod
    def register(cls, datasource_class: Type[BaseDatasource] = None, priority: int = 100):
        """Decorator used to register a BaseDatasource based class (from now on "Datasources")
        on the Datasources local storage, accessed as singleton.

        :param datasource_class: the BaseDatasource based class (not an instance of the class, but the class itself).
            This should be used as decorator, rather than called directly.
        :param priority: priority of the Datasource, as int. Used to sort which Datasources will be used.
            Datasources with higher numbers are returned first. Default priority value is 100.
        """
        if not datasource_class:
            def wrapper(_datasource_class: Type[BaseDatasource]):
                cls.register(
                    datasource_class=_datasource_class,
                    priority=priority,
                )
                return _datasource_class
            return wrapper

        cls._datasources[datasource_class] = priority
        cls._datasources_sorted.append(datasource_class)
        cls._datasources_sorted.sort(reverse=True, key=lambda _datasource_class: cls._datasources[_datasource_class])
        return datasource_class

    @classmethod
    def get_datasources(cls) -> List[Type[BaseDatasource]]:
        """Get the BaseDatasource based classes registered on the Datasources local storage, sorted by priority,
        with the higher priority Datasources first.
        """
        return cls._datasources_sorted

    @classmethod
    def reset(cls):
        """Reset the Datasources local storage. This is usually called from tests.
        """
        cls._datasources = dict()
        cls._datasources_sorted = list()
