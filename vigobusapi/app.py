"""APP
Module with all the available endpoints and the FastAPI initialization.
"""

# # Native # #
import asyncio

# # Installed # #
import uvicorn
import fastapi

# # Package # #
from .entities import *
from .error_handler import *
from .settings_handler import settings
from .vigobus_getters import get_stop, get_buses

__all__ = ("app", "run")

app = fastapi.FastAPI(
    title=settings.api_name,
    description=settings.api_description,
    version=settings.api_version
)


@app.get("/stop/{stop_id}", response_model=Stop)
async def endpoint_get_stop(stop_id: int):
    """Endpoint to get information of a Stop giving the Stop ID
    """
    with manage_endpoint_exceptions():
        stop: Stop = await asyncio.wait_for(
            get_stop(stop_id),
            timeout=settings.endpoint_timeout
        )
        return stop.dict()


@app.get("/buses/{stop_id}", response_model=BusesResponse)
async def endpoint_get_buses(stop_id: int, get_all_buses: bool = False):
    """Endpoint to get a list of Buses coming to a Stop giving the Stop ID.
    By default the shortest available list of buses is returned, unless 'get_all_buses' param is True
    """
    with manage_endpoint_exceptions():
        buses_result: BusesResponse = await asyncio.wait_for(
            get_buses(stop_id, get_all_buses),
            timeout=settings.endpoint_timeout
        )
        return buses_result.dict()


def run():
    """Run the API using Uvicorn
    """
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level
    )


if __name__ == '__main__':
    run()
