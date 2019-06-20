"""APP
Module with all the available endpoints and the FastAPI initialization.
"""

# # Native # #
import asyncio
import contextlib

# # Installed # #
import uvicorn
import fastapi
from pybusent import Stop, StopNotExist, BusesResult
from requests_async import RequestException, Timeout
# noinspection PyPackageRequirements
from starlette import status as statuscode

# # Project # #
from vigobusapi.settings_handler import load_settings
from vigobusapi.settings_handler.const import *

# # Package # #
from .vigobus_getters import get_stop, get_buses, ParseError

__all__ = ("app", "run")

settings = load_settings()

app = fastapi.FastAPI(
    title=settings[API_NAME],
    description=settings[API_DESCRIPTION],
    version=settings[API_VERSION]
)


@contextlib.contextmanager
def manage_endpoint_exceptions():
    """ContextManager to catch exceptions that can be raised when getting information from external data sources,
    and return an HTTP Status Code to the client depending on the exception raised.
    """
    try:
        yield
    except (Timeout, asyncio.TimeoutError):
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_408_REQUEST_TIMEOUT, detail="Timeout on external source"
        )
    except RequestException:
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR, detail="Generic HTTP error on external source"
        )
    except ParseError:
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing external source data"
        )
    except StopNotExist:
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_404_NOT_FOUND, detail="Stop not exists"
        )


@app.get("/stop/{stop_id}")
async def endpoint_get_stop(stop_id: int):
    """Endpoint to get information of a Stop giving the Stop ID
    """
    with manage_endpoint_exceptions():
        stop: Stop = await asyncio.wait_for(
            get_stop(stop_id),
            timeout=settings[ENDPOINT_TIMEOUT]
        )
        return stop.get_dict()


@app.get("/buses/{stop_id}")
async def endpoint_get_buses(stop_id: int, get_all_buses: bool = False):
    """Endpoint to get a list of Buses coming to a Stop giving the Stop ID.
    By default the shortest available list of buses is returned, unless 'get_all_buses' param is True
    """
    with manage_endpoint_exceptions():
        buses_result: BusesResult = await asyncio.wait_for(
            get_buses(stop_id, get_all_buses),
            timeout=settings[ENDPOINT_TIMEOUT]
        )
        return buses_result.get_dict()


def run():
    """Run the API using Uvicorn
    """
    uvicorn.run(app, host=settings[API_HOST], port=settings[API_PORT], log_level=settings[API_LOG_LEVEL])


if __name__ == '__main__':
    run()
