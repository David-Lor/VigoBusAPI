"""CACHE DATA SOURCE
Cached local storages with TTL for Stops and Buses
"""

# # Native # #
from typing import Optional

# # Installed # #
from cachetools import TTLCache

# # Project # #
from vigobusapi.settings import settings
from vigobusapi.entities import BusesResponse
from vigobusapi.logger import logger

__all__ = ("buses_cache", "save_buses", "get_buses")

buses_cache = TTLCache(maxsize=settings.buses_cache_maxsize, ttl=settings.buses_cache_ttl)
"""Buses Cache. Key: tuple (Stop ID, bool GetAllBuses?). Value: BusesResponse"""


def save_buses(stop_id: int, get_all_buses: bool, buses_result: BusesResponse):
    """This function must be executed whenever a List of Buses for a Stop is found by any getter,
    other than the Stops Cache
    """
    buses_cache[(stop_id, get_all_buses)] = buses_result
    logger.debug(f"Saved buses on local cache")


def get_buses(stop_id: int, get_all_buses: bool) -> Optional[BusesResponse]:
    """Get List of Buses from the Buses Cache, by Stop ID and All Buses wanted (True/False).
    If the list of buses for the given Stop ID is not cached, None is returned.
    """
    buses_result: Optional[BusesResponse] = buses_cache.get((stop_id, get_all_buses))
    logger.debug(f"Buses {'found' if buses_result else 'not found'} on local cache")

    if buses_result is None and not get_all_buses:
        # If NOT All Buses are requested, and a Not All Buses query is not cached, but an All Buses query is cached,
        #  return it, since it is still valid - but limit the results
        buses_result = buses_cache.get((stop_id, True))
        if buses_result and len(buses_result.buses) > settings.buses_normal_limit:
            buses_result = buses_result.copy()
            buses_result.buses = buses_result.buses[:settings.buses_normal_limit]
            buses_result.more_buses_available = True
            logger.debug(f"Buses from a getAllBuses=True request found on local cache, valid for this request")

    return buses_result
