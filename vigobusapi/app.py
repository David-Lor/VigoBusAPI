
# # Native # #
from asyncio import TimeoutError

# # Installed # #
from fastapi import FastAPI, HTTPException
from requests_async import HTTPError
# noinspection PyPackageRequirements
from starlette.status import HTTP_408_REQUEST_TIMEOUT, HTTP_500_INTERNAL_SERVER_ERROR
from pybuses import StopNotExist, GetterResourceUnavailable

# # Project # #
from vigobusapi.settings_handler import load_settings
from vigobusapi.settings_handler.const import *

# # Package # #
from .vigobus_getters import html
from .json_generator import stop_to_json


settings = load_settings()

app = FastAPI(
    title=settings[API_NAME],
    description=settings[API_DESCRIPTION],
    version=settings[API_VERSION]
)


@app.get("/stop/{stop_id}")
async def get_stop(stop_id: int):
    try:
        stop = await html.get_stop(stop_id)
    except TimeoutError:
        raise HTTPException(status_code=HTTP_408_REQUEST_TIMEOUT, detail="Timeout on external source")
    except HTTPError:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Generic HTTP error on external source")
    except GetterResourceUnavailable:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    except StopNotExist:
        stop = None
    return stop_to_json(stop)
