"""STOPS & BUSES Routes
"""

# # Native # #
from typing import Optional, Set

# # Installed # #
from fastapi import APIRouter, Query, HTTPException

# # Project # #
from vigobusapi.entities import Stop, Stops, BusesResponse
from vigobusapi.vigobus_getters import get_stop, get_stops, get_buses, search_stops
from vigobusapi.logger import logger

__all__ = ("router",)

router = APIRouter()


@router.get("/stops", response_model=Stops)
async def endpoint_get_stops(
        stop_name: Optional[str] = Query(None),
        limit: Optional[int] = Query(None),
        stops_ids: Optional[Set[int]] = Query(None, alias="stop_id")
):
    """Endpoint to search/list stops by different filters. Only one filter can be used.
    Returns 400 if no filters given.
    The filters available are:

    - stop_name: search by a single string in stop names. "limit" can be used for limiting results size.
    - stop_id: repeatable param for getting multiple stops by id on a single request. Not found errors are ignored.
    """
    with logger.contextualize(**locals()):
        if stop_name is not None:
            stops = await search_stops(stop_name=stop_name, limit=limit)
        elif stops_ids:
            stops = await get_stops(stops_ids)
        else:
            raise HTTPException(status_code=400, detail="No filters given")
        return [stop.dict() for stop in stops]


@router.get("/stop/{stop_id}", response_model=Stop)
@router.get("/stops/{stop_id}", response_model=Stop)
async def endpoint_get_stop(stop_id: int):
    """Endpoint to get information of a Stop giving the Stop ID
    """
    with logger.contextualize(**locals()):
        stop = await get_stop(stop_id)
        return stop.dict()


@router.get("/buses/{stop_id}", response_model=BusesResponse)
@router.get("/stops/{stop_id}/buses", response_model=BusesResponse)
async def endpoint_get_buses(stop_id: int, get_all_buses: bool = False):
    """Endpoint to get a list of Buses coming to a Stop giving the Stop ID.
    By default the shortest available list of buses is returned, unless 'get_all_buses' param is True
    """
    with logger.contextualize(**locals()):
        buses_result = await get_buses(stop_id, get_all_buses=get_all_buses)
        return buses_result.dict()