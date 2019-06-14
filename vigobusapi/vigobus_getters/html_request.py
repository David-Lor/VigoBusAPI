"""HTML_REQUEST
Async Functions to request the HTML external data source and return the raw result returned by the source.
"""

# # Native # #
from typing import Dict, Optional
import copy

# # Installed # #
from requests_async import get, post, Response, RequestException

# # Project # #
from vigobusapi.settings_handler import load_settings
from vigobusapi.settings_handler.const import *

# # Package # #
from .html_const import *

__all__ = ("request_html",)

settings = load_settings()


async def request_html(stopid: int, page: Optional[int] = None, extra_params: Optional[Dict] = None) -> str:
    """Async function to request the webpage data source, returning the HTML content.
    :param stopid: Stop ID
    :param page: Page to retrieve (default=None, so first page)
    :param extra_params: Additional parameters required by the data source when asking for a certain page higher than 1
                         (__VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION), as dict
    :raises: requests_async.RequestTimeout | requests_async.RequestException
    """
    # Generate params (Stop ID)
    params = {"parada": stopid}

    # Extra params available = next pages, requiring body & updated headers
    if extra_params is not None:
        # Body/Data
        extra_params[EXTRA_DATA_PAGE] = page  # add the Page number to the extra_params
        body = EXTRA_DATA.format(**extra_params)  # format the request Body with the extra_params
        # Headers
        headers = copy.deepcopy(HEADERS)
        headers.update(HEADERS_NEXT_LOADS)  # update the original Headers with the extra items used on next pages
        headers[HEADERS_NEXT_LOADS_REFERER] = settings[HTTP_REMOTE_API] + HEADERS_NEXT_LOADS_REFERER_PARAMS.format(
            stopid=stopid  # update the Referer header with the URL with the stopid as parameter
        )
    # Extra params not available = this is the first page, body not required & use unmodified headers
    else:
        headers = HEADERS
        body = None

    # Getting first page is GET request, getting other pages is POST request
    method = get if page is None else post
    last_error = None

    # Run the Requests, with Retries support
    for i in range(settings[HTTP_RETRIES]):
        try:
            response: Response = await method(
                url=settings[HTTP_REMOTE_API],
                params=params,
                data=body,
                headers=headers,
                timeout=settings[HTTP_TIMEOUT]
            )
            response.raise_for_status()
            return response.text
        except RequestException as ex:
            last_error = ex

    raise last_error
