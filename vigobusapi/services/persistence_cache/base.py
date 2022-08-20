import abc
from typing import Optional

from ...settings import PersistenceSettings
import vigobus.models



class BaseRepositoryCache(abc.ABC):

    @abc.abstractmethod
    def __init__(self, settings: PersistenceSettings):
        pass

    @abc.abstractmethod
    async def get_stop(self, stop_id: int) -> Optional[vigobus.models.Stop]:
        pass
