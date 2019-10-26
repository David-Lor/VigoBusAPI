"""WSDL
Async functions to fetch data from the WSDL external data source and parse them to return the final objects.
"""

# # Installed # #
from requests_async import HTTPError

# # Package # #
from .wsdl_request import request_wsdl_stop
from .wsdl_parser import parse_xml_stop, parse_xml_error_stop_not_exist

# # Project # #
from ...entities import *
from ...exceptions import *

__all__ = ("get_stop",)


async def get_stop(stop_id: int) -> Stop:
    """Async function to get information of a Stop (name & location) from the WSDL API.
    :raises: requests_async.RequestTimeout | requests_async.RequestException | exceptions.StopNotExist
    """
    try:
        xml = await request_wsdl_stop(stop_id)

    except HTTPError as request_error:
        # When the Stop not exists, the WSDL API returns 500 causing a HTTPError
        # We use the following parser helper to check if the API returned an error because the stop not exists
        if parse_xml_error_stop_not_exist(request_error.response.text):
            raise StopNotExist()
        else:
            raise request_error

    else:
        return parse_xml_stop(xml)
