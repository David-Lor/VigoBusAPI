"""APP
Module with all the available endpoints and the FastAPI initialization.
"""

# # Native # #
import asyncio

# # Installed # #
import uvicorn
import fastapi
from pybuses_entities import StopNotExist
from requests_async import RequestException, Timeout
# noinspection PyPackageRequirements
from starlette.status import HTTP_408_REQUEST_TIMEOUT, HTTP_500_INTERNAL_SERVER_ERROR

# # Project # #
from vigobusapi.settings_handler import load_settings
from vigobusapi.settings_handler.const import *

# # Package # #
from .vigobus_getters import get_stop, get_buses, ParseError
from .json_generator import stop_to_json, buses_to_json

__all__ = ("app", "run")

settings = load_settings()

app = fastapi.FastAPI(
    title=settings[API_NAME],
    description=settings[API_DESCRIPTION],
    version=settings[API_VERSION]
)


@app.get("/stop/{stop_id}")
async def endpoint_get_stop(stop_id: int):
    """Endpoint to get information of a Stop giving the Stop ID
    """
    # TODO try-except-except-except... with a context manager/decorator?
    try:
        stop = await asyncio.wait_for(
            get_stop(stop_id),
            timeout=settings[ENDPOINT_TIMEOUT]
        )
    except (Timeout, asyncio.TimeoutError):
        raise fastapi.HTTPException(
            status_code=HTTP_408_REQUEST_TIMEOUT, detail="Timeout on external source"
        )
    except RequestException:
        raise fastapi.HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Generic HTTP error on external source"
        )
    except ParseError:
        raise fastapi.HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing external source data"
        )
    except StopNotExist:
        stop = None
    return stop_to_json(stop)


@app.get("/buses/{stop_id}")
async def endpoint_get_buses(stop_id: int, get_all_buses: bool = False):
    """Endpoint to get a list of Buses coming to a Stop giving the Stop ID.
    By default the shortest available list of buses is returned, unless 'get_all_buses' param is True
    """
    # TODO try-except-except-except... with a context manager/decorator?
    buses = list()
    stop_exists = True
    try:
        buses = await asyncio.wait_for(
            get_buses(stop_id, get_all_buses),
            timeout=settings[ENDPOINT_TIMEOUT]
        )
    except (Timeout, asyncio.TimeoutError):
        raise fastapi.HTTPException(
            status_code=HTTP_408_REQUEST_TIMEOUT, detail="Timeout on external source"
        )
    except RequestException:
        raise fastapi.HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Generic HTTP error on external source"
        )
    except ParseError:
        raise fastapi.HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing external source data"
        )
    except StopNotExist:
        stop_exists = False
    return buses_to_json(buses, stop_exists)


def run():
    """Run the API using Uvicorn
    """
    uvicorn.run(app, host=settings[API_HOST], port=settings[API_PORT], log_level=settings[API_LOG_LEVEL])


if __name__ == '__main__':
    run()
