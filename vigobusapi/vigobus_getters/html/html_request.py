"""HTML_REQUEST
Async Functions to request the HTML external data source and return the raw result returned by the source.
"""

# # Native # #
from typing import Dict, Optional
import copy

# # Package # #
from .html_const import *

# # Project # #
from vigobusapi.support_services import http_request
from vigobusapi.settings import settings

__all__ = ("request_html",)

ENDPOINT_URL = "http://infobus.vitrasa.es:8002/Default.aspx"


async def request_html(stop_id: int, page: Optional[int] = None, extra_params: Optional[Dict] = None) -> str:
    """Async function to request the webpage data source, returning the HTML content.
    :param stop_id: Stop ID
    :param page: Page to retrieve (default=None, so first page)
    :param extra_params: Additional parameters required by the data source when asking for a certain page higher than 1
                         (__VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION), as dict
    :raises: requests_async.RequestTimeout | requests_async.RequestException
    """
    # URL query params (Stop ID)
    params = {"parada": stop_id}

    if extra_params is not None:
        # Extra params available = next pages, requiring body & updated headers

        # Body/Data
        extra_params[EXTRA_DATA_PAGE] = page  # add the Page number to the extra_params
        body = EXTRA_DATA.format(**extra_params)  # format the request Body with the extra_params

        # Headers
        headers = copy.deepcopy(HEADERS)
        headers.update(HEADERS_NEXT_LOADS)  # update the original Headers with the extra items used on next pages
        headers[HEADERS_NEXT_LOADS_REFERER] = ENDPOINT_URL + HEADERS_NEXT_LOADS_REFERER_PARAMS.format(
            stop_id=stop_id  # update the Referer header with the URL with the stop_id as parameter
        )

    else:
        # Extra params not available = this is the first page, body not required & use unmodified headers
        headers = HEADERS
        body = None

    # Getting first page is GET request, getting other pages is POST request
    method = "GET" if page is None else "POST"

    response = await http_request(
        method=method,
        params=params,
        body=body,
        headers=headers,
        url=ENDPOINT_URL
    )
    return response.text
