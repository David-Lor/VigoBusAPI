"""HTML_REQUEST
Async Functions to request the HTML external data source and return the raw result returned by the source.
"""

# # Installed # #
from requests_async import get, Response

# # Project # #
from vigobusapi.settings_handler import load_settings
from vigobusapi.settings_handler.const import *

__all__ = ("request_html",)

settings = load_settings()


async def request_html(stopid: int) -> str:
    """Async function to request the webpage data source, returning the HTML content.
    :raises: requests_async.RequestTimeout | requests_async.RequestException
    """
    response: Response = await get(settings[HTTP_REMOTE_API] + str(stopid), timeout=settings[HTTP_TIMEOUT])
    response.raise_for_status()
    return response.text
