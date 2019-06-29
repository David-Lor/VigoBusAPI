
# # Native # #
import html

# # Installed # #
from requests_async import post, Response

# # Project # #
from vigobusapi.settings_handler import settings

# # Package # #
from .wsdl_const import *

__all__ = ("request_wsdl_stop",)


async def request_wsdl_stop(stopid: int) -> str:
    """Async function to request the WSDL API, Stop endpoint, returning the XML response.
    :raises: requests_async.RequestTimeout | requests_async.RequestException
    """
    response: Response = await post(
        url=settings.wsdl_remote_api,
        data=GET_STOP_BODY.format(stop_id=stopid),
        headers=HEADERS,
        timeout=settings.wsdl_timeout
    )
    response.raise_for_status()
    return html.unescape(response.text)


# async def request_wsdl_buses(stopid: int) -> str:
#     """Async function to request the WSDL API, Buses endpoint, returning the XML response.
#     :raises: requests_async.RequestTimeout | requests_async.RequestException
#     """
#     response: Response = await post(
#         url=settings[WSDL_REMOTE_API],
#         data=GET_BUSES_BODY.format(stop_id=stopid),
#         headers=HEADERS,
#         timeout=settings[WSDL_TIMEOUT]
#     )
#     response.raise_for_status()
#     return html.unescape(response.text)


# async def request_wsdl_near_stops(lat: float, lon: float) -> str:
#     """Async function to request the WSDL API, Near Stops endpoint, returning the XML response.
#     :raises: requests_async.RequestTimeout | requests_async.RequestException
#     """
#     response: Response = await post(
#         url=settings[WSDL_REMOTE_API],
#         data=GET_NEAR_STOPS_BODY.format(lat=lat, lon=lon),
#         headers=HEADERS,
#         timeout=settings[WSDL_TIMEOUT]
#     )
#     response.raise_for_status()
#     return html.unescape(response.text)
