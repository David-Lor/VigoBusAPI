"""ERROR HANDLER
Handle exceptions occurred on endpoints
"""

# # Native # #
import asyncio
import contextlib
import traceback

# # Installed # #
import fastapi
from requests_async import RequestException, Timeout
from starlette import status as statuscode

# # Package # #
from .exceptions import *
from .vigobus_getters.exceptions import *

__all__ = ("manage_endpoint_exceptions",)


@contextlib.contextmanager
def manage_endpoint_exceptions():
    """ContextManager to catch exceptions that can be raised when getting information from external data sources,
    returning a HTTP Status Code to the client depending on the exception raised.
    """
    try:
        yield
    except StopNotExist:
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_404_NOT_FOUND, detail="Stop not exists"
        )
    except (Timeout, asyncio.TimeoutError):
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_408_REQUEST_TIMEOUT, detail="Timeout on external source"
        )
    except RequestException:
        traceback.print_exc()
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR, detail="Generic HTTP error on external source"
        )
    except ParseError:
        traceback.print_exc()
        raise fastapi.HTTPException(
            status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing external source data"
        )
