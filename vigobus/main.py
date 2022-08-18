from typing import Optional, List

from .datasources.base import BaseDatasource, Datasources
from .exceptions import DatasourceMethodUnavailableException, StopNotExistException
from .models import Stop, BusesResponse
from .utils import ErrorRetrier

__all__ = ("Vigobus",)


class Vigobus(BaseDatasource):
    """Main class that provides the methods to fetch VigoBus data.

    The Vigobus class internally calls all the available Datasources, in their respective order,
    to fetch the requested data. If any datasource does not provide the requested data, or an exception occurs,
    the next datasource is used, until no more datasources are available.
    """

    _datasources: List[BaseDatasource] = []

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_datasources()

    async def get_all_stops(self) -> List[Stop]:
        retrier = self._get_error_retrier()
        for datasource in self._datasources:
            with retrier.wrap():
                return await datasource.get_all_stops()
        retrier.raise_last_exception()

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        retrier = self._get_error_retrier()
        for datasource in self._datasources:
            with retrier.wrap():
                return await datasource.get_stop(stop_id)
        retrier.raise_last_exception()

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        retrier = self._get_error_retrier()
        for datasource in self._datasources:
            with retrier.wrap():
                try:
                    return await datasource.get_buses(stop_id, get_all_buses)
                except StopNotExistException as ex:
                    retrier.add_exception(ex)
                    break
        retrier.raise_last_exception()

    def _initialize_datasources(self):
        """Instance each available Datasource class, with the same attributes as the current class instance.
        """
        data = self.dict()
        for datasource_cls in Datasources.get_datasources():
            self._datasources.append(datasource_cls(**data))

    @staticmethod
    def _get_error_retrier():
        return ErrorRetrier(DatasourceMethodUnavailableException)
