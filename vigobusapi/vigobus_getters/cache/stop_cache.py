"""CACHE DATA SOURCE
Cached local storages with TTL for Stops and Buses
"""

# # Native # #
from typing import Optional

# # Installed # #
from cachetools import TTLCache

# # Project # #
from vigobusapi.settings import settings
from vigobusapi.exceptions import StopNotExist
from vigobusapi.entities import Stop, StopOrNotExist
from vigobusapi.logger import logger

__all__ = ("stops_cache", "save_stop", "save_stop_not_exist", "get_stop")

stops_cache = TTLCache(maxsize=settings.stops_cache_maxsize, ttl=settings.stops_cache_ttl)
"""Stops Cache. Key: Stop ID. Value: Stop object OR StopNotExist exception object."""


def save_stop(stop: Stop):
    """This function must be executed whenever a Stop is found by any getter, other than the Stops Cache
    """
    stops_cache[stop.stop_id] = stop
    logger.debug("Saved stop on local cache")


def save_stop_not_exist(stop_id: int):
    """This function must be executed whenever an external data source reports that a Stop Not Exists
    """
    stops_cache[stop_id] = StopNotExist()
    logger.debug("Saved stop as non existing on local cache")


def get_stop(stop_id: int) -> Optional[StopOrNotExist]:
    """Get a Stop from the Stops Cache.
    If the Stop does not exist and this was cached, StopNotExist exception is returned (not raised).
    If the Stop is not cached, None is returned.
    """
    stop = stops_cache.get(stop_id)
    logger.debug(f"Stop {'found' if stop else 'not found'} on local cache")
    return stop
