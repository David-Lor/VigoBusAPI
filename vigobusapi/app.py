"""APP
Module with all the available endpoints and the FastAPI initialization.
"""

# # Native # #
from typing import Optional

# # Installed # #
import uvicorn
from fastapi import FastAPI, Response

# # Package # #
from vigobusapi.entities import Stop, Stops, BusesResponse
from vigobusapi.request_handler import request_handler
from vigobusapi.settings_handler import settings
from vigobusapi.vigobus_getters import get_stop, get_buses, search_stops
from vigobusapi.logger import logger

__all__ = ("app", "run")

app = FastAPI(
    title=settings.api_name
)

app.middleware("http")(request_handler)


@app.get("/status")
async def endpoint_status():
    return Response(
        content="OK",
        media_type="text/plain",
        status_code=200
    )


@app.get("/stops", response_model=Stops)
async def endpoint_get_stops(stop_name: str, limit: Optional[int] = None):
    """Endpoint to search stops by a given name
    """
    with logger.contextualize(**locals()):
        stops = await search_stops(stop_name=stop_name, limit=limit)
        return [stop.dict() for stop in stops]


@app.get("/stop/{stop_id}", response_model=Stop)
async def endpoint_get_stop(stop_id: int):
    """Endpoint to get information of a Stop giving the Stop ID
    """
    with logger.contextualize(**locals()):
        stop = await get_stop(stop_id)
        return stop.dict()


@app.get("/buses/{stop_id}", response_model=BusesResponse)
async def endpoint_get_buses(stop_id: int, get_all_buses: bool = False):
    """Endpoint to get a list of Buses coming to a Stop giving the Stop ID.
    By default the shortest available list of buses is returned, unless 'get_all_buses' param is True
    """
    with logger.contextualize(**locals()):
        buses_result = await get_buses(stop_id, get_all_buses=get_all_buses)
        return buses_result.dict()


def run():
    """Run the API using Uvicorn
    """
    logger.info("Running the app with uvicorn")

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level
    )


if __name__ == '__main__':
    run()
