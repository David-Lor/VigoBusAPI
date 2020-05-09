"""ERROR HANDLER
Handle exceptions occurred on endpoints
"""

# # Native # #
import asyncio
import traceback

# # Installed # #
from fastapi import status as statuscode
from fastapi.responses import JSONResponse
from requests_async import RequestException, Timeout, ConnectTimeout

# # Package # #
from vigobusapi.exceptions import *
from vigobusapi.vigobus_getters.exceptions import *
from vigobusapi.logger import logger

__all__ = ("handle_exception",)


class Responses:
    stop_not_exists = JSONResponse(
        status_code=statuscode.HTTP_404_NOT_FOUND,
        content={"detail": "Stop not exists"}
    )
    external_source_timeout = JSONResponse(
        status_code=statuscode.HTTP_408_REQUEST_TIMEOUT,
        content={"detail": "Timeout on external source"}
    )
    external_source_error = JSONResponse(
        status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Generic HTTP error on external source"}
    )
    parsing_error = JSONResponse(
        status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error parsing external source data"}
    )
    generic_error = JSONResponse(
        status_code=statuscode.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unknown internal error"}
    )


EXCEPTIONS_RESPONSES = {
    StopNotExist: Responses.stop_not_exists,
    Timeout: Responses.external_source_timeout,
    asyncio.TimeoutError: Responses.external_source_timeout,
    RequestException: Responses.external_source_error,
    ParseError: Responses.parsing_error
}
"""Relation between exceptions and the response to return. Exception class inheritance is supported"""

EXCEPTIONS_NO_ERROR_LOG = (StopNotExist, Timeout, asyncio.TimeoutError)
"""Exceptions that will not log an error"""


def handle_exception(exception):
    try:
        response = next(
            response for exception_iter, response in EXCEPTIONS_RESPONSES.items()
            if isinstance(exception, exception_iter)
        )
    except StopIteration:
        response = Responses.generic_error

    try:
        next(exception_iter for exception_iter in EXCEPTIONS_NO_ERROR_LOG if isinstance(exception, exception_iter))
    except StopIteration:
        logger.exception("Error on request")

    return response
