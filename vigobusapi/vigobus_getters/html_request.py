"""HTML_REQUEST
Async Functions to request the HTML external data source and return the raw result returned by the source.
"""

# # Native # #
from typing import Dict, Optional

# # Installed # #
from requests_async import get, post, Response

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

    # Generate body if required
    body = None
    if extra_params is not None:
        extra_params[EXTRA_DATA_PAGE] = page
        body = EXTRA_DATA.format(**extra_params)

    # Getting first page is GET request, getting other pages is POST request
    method = get if page is None else post

    response: Response = await method(
        url=settings[HTTP_REMOTE_API],
        params=params,
        data=body,
        headers=HEADERS,
        timeout=settings[HTTP_TIMEOUT]
    )
    response.raise_for_status()
    return response.text
