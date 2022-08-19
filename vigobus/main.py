from typing import Optional, List, Dict, Type, Any

import pydantic

from .datasources.base import BaseDatasource
from .datasources.ds_vigoapi import DatasourceVigoApi
from .datasources.ds_vigoopendata import DatasourceVigoOpenData
from .exceptions import DatasourceMethodUnavailableException, StopNotExistException
from .models import Stop, BusesResponse
from .utils import Utils, ErrorRetrier

__all__ = ("Vigobus",)


class Vigobus(BaseDatasource):
    """Main class that provides the methods to fetch VigoBus data.

    The Vigobus class internally calls all the available Datasources, in their respective order,
    to fetch the requested data. If any datasource does not provide the requested data, or an exception occurs,
    the next datasource is used, until no more datasources are available.
    """

    # datasources_* are static lists with the Datasources classes (not instances) that can resolve each method.
    # The order in which Datasources are defined in these lists, are the order in which they are queried
    # (if a Datasource fails, the next one is queried).

    datasources_getallstops: List[Type[BaseDatasource]] = [DatasourceVigoOpenData]
    datasources_getstop: List[Type[BaseDatasource]] = [DatasourceVigoApi]
    datasources_getbuses: List[Type[BaseDatasource]] = [DatasourceVigoApi]

    _datasources: Dict[Type[BaseDatasource], BaseDatasource] = pydantic.PrivateAttr(default_factory=dict)
    """All the Datasources classes from datasources_* lists are instanced when Vigobus() is instanced,
    and placed on this dict, keyed by their class type, so we can use the methods from each instance.
    """
    _iter_datasources_cache: Dict[Any, List[BaseDatasource]] = pydantic.PrivateAttr(default_factory=dict)
    """Cache of returns from the _iter_datasource() method, keyed by the method based on args."""

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_datasources()

    async def get_all_stops(self) -> List[Stop]:
        retrier = self._get_error_retrier()
        for datasource in self._iter_datasources(self.datasources_getallstops):
            with retrier.wrap():
                return await datasource.get_all_stops()
        retrier.raise_last_exception()

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        retrier = self._get_error_retrier()
        for datasource in self._iter_datasources(self.datasources_getstop):
            with retrier.wrap():
                return await datasource.get_stop(stop_id)
        retrier.raise_last_exception()

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        retrier = self._get_error_retrier()
        for datasource in self._iter_datasources(self.datasources_getbuses):
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
        kwargs = self.dict()
        datasources_classes = [v for k, v in kwargs.items() if k.startswith("datasources_")]
        datasources_classes = Utils.flatten(datasources_classes, return_as=set)
        self._datasources = {cls: cls(**kwargs) for cls in datasources_classes}

    def _iter_datasources(self, datasources_classes: List[Type[BaseDatasource]]) -> List[BaseDatasource]:
        # TODO Review if the caching is useful or more expensive
        cache_key = tuple(datasources_classes)
        try:
            return self._iter_datasources_cache[cache_key]
        except KeyError:
            result = [instance for cls, instance in self._datasources.items() if cls in datasources_classes]
            self._iter_datasources_cache[cache_key] = result
            return result

    @staticmethod
    def _get_error_retrier():
        return ErrorRetrier(DatasourceMethodUnavailableException)
