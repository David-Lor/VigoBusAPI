"""REQUEST HANDLER
Decorator used on all the endpoint handler functions, for error & log handling
"""

# # Native # #
import time
import asyncio
from uuid import uuid4

# # Installed # #
from fastapi import Request, Response

# # Project # #
from vigobusapi.error_handler import handle_exception
from vigobusapi.settings_handler import settings
from vigobusapi.logger import logger


async def request_handler(request: Request, call_next):
    """Middleware used on FastAPI to process each request, for error & log handling
    """
    url = str(request.url)
    if url.endswith("/favicon.ico"):
        return Response(status_code=404)

    request_id = str(uuid4())
    with logger.contextualize(request_id=request_id, url=url):
        start_time = time.time()

        # noinspection PyBroadException
        try:
            logger.info("Request started")
            return await asyncio.wait_for(
                call_next(request),
                timeout=settings.endpoint_timeout
            )

        except Exception as exception:
            return handle_exception(exception)

        finally:
            process_time = round(time.time() - start_time, ndigits=5)
            logger.bind(last_record=True, process_time=process_time).info(f"Request ended in {process_time} seconds")
