"""HTML_REQUEST
Async Functions to request the HTML external data source and return the raw result returned by the source.
"""

# # Native # #
from typing import Dict, Optional
import copy
import time

# # Installed # #
from requests_async import get, post, Response, RequestException

# # Package # #
from .html_const import *

# # Project # #
from vigobusapi.settings_handler import settings
from vigobusapi.logger import logger

__all__ = ("request_html",)


async def request_html(stop_id: int, page: Optional[int] = None, extra_params: Optional[Dict] = None) -> str:
    """Async function to request the webpage data source, returning the HTML content.
    :param stop_id: Stop ID
    :param page: Page to retrieve (default=None, so first page)
    :param extra_params: Additional parameters required by the data source when asking for a certain page higher than 1
                         (__VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION), as dict
    :raises: requests_async.RequestTimeout | requests_async.RequestException
    """
    # Generate params (Stop ID)
    params = {"parada": stop_id}

    # Extra params available = next pages, requiring body & updated headers
    if extra_params is not None:
        # Body/Data
        extra_params[EXTRA_DATA_PAGE] = page  # add the Page number to the extra_params
        body = EXTRA_DATA.format(**extra_params)  # format the request Body with the extra_params
        # Headers
        headers = copy.deepcopy(HEADERS)
        headers.update(HEADERS_NEXT_LOADS)  # update the original Headers with the extra items used on next pages
        headers[HEADERS_NEXT_LOADS_REFERER] = settings.html_remote_api + HEADERS_NEXT_LOADS_REFERER_PARAMS.format(
            stop_id=stop_id  # update the Referer header with the URL with the stop_id as parameter
        )
    # Extra params not available = this is the first page, body not required & use unmodified headers
    else:
        headers = HEADERS
        body = None

    # Getting first page is GET request, getting other pages is POST request
    method = get if page is None else post
    last_error = None

    # Run the Requests, with Retries support
    retries = settings.http_retries
    url = settings.html_remote_api
    timeout = settings.http_timeout

    for i in range(retries):
        with logger.contextualize(
                request_url=url,
                request_attempt=i+1,
                request_max_attempts=retries,
                request_params=params,
                request_body=body,
                request_headers=headers,
                request_timeout=timeout
        ):
            logger.debug("Requesting URL")

            try:
                start_time = time.time()
                response: Response = await method(
                    url=url,
                    params=params,
                    data=body,
                    headers=headers,
                    timeout=timeout
                )

                response_time = round(time.time() - start_time, 4)
                logger.bind(
                    response_elapsed_time=response_time,
                    response_status_code=response.status_code,
                    response_body=response.text
                ).debug("Response received")

                response.raise_for_status()
                return response.text

            except RequestException as ex:
                logger.warning("Request failed")
                last_error = ex

    raise last_error
