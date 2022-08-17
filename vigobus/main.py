from typing import Optional, List

from .datasources.base import BaseDatasource, Datasources
from .exceptions import DatasourceMethodUnavailableException, StopNotExistException
from .models import Stop, BusesResponse

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

    # TODO combine common datasource-try-except iteration logic.

    # TODO last_ex should no raise DatasourceMethodUnavailableException when previous error/s were different.

    async def get_all_stops(self) -> List[Stop]:
        last_ex = None
        for datasource in self._datasources:
            try:
                result = await datasource.get_all_stops()
                return result

            except Exception as ex:
                last_ex = ex
                if isinstance(ex, DatasourceMethodUnavailableException):
                    continue

        raise last_ex

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        last_ex = None
        for datasource in self._datasources:
            try:
                result = await datasource.get_stop(stop_id)
                return result

            except Exception as ex:
                last_ex = ex
                if isinstance(ex, DatasourceMethodUnavailableException):
                    continue

        raise last_ex

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        last_ex = None
        for datasource in self._datasources:
            try:
                result = await datasource.get_buses(stop_id, get_all_buses)
                return result

            except Exception as ex:
                last_ex = ex
                if isinstance(ex, DatasourceMethodUnavailableException):
                    continue
                if isinstance(ex, StopNotExistException):
                    break

        raise last_ex

    def _initialize_datasources(self):
        """Instance each available Datasource class, with the same attributes as the current class instance.
        """
        data = self.dict()
        for datasource_cls in Datasources.get_datasources():
            self._datasources.append(datasource_cls(**data))
