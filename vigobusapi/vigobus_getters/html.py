
# # Native # #
from typing import List

# # Installed # #
from pybuses import Stop, Bus

# # Package # #
from .html_request import request_html
from .html_parser import parse_html


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :raises: asyncio.TimeoutError | requests_async.HTTPError | pybuses.StopNotExist | pybuses.GetterResourceUnavailable
    """
    html = await request_html(stopid)
    return parse_html(content=html, buses=False)


async def get_buses(stopid: int) -> List[Bus]:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    :raises: asyncio.TimeoutError | requests_async.HTTPError | pybuses.StopNotExist | pybuses.GetterResourceUnavailable
    """
    html = await request_html(stopid)
    return parse_html(content=html, buses=True)
