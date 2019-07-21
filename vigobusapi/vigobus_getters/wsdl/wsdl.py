"""WSDL
Async functions to fetch data from the WSDL external data source and parse them to return the final objects.
"""

# # Installed # #
from pybusent import StopNotExist
from requests_async import HTTPError

# # Parent Package # #
from ..entities import Stop

# # Package # #
from .wsdl_request import request_wsdl_stop
from .wsdl_parser import parse_xml_stop, parse_xml_error_stop_not_exist


__all__ = ("get_stop",)


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (name & location) from the WSDL API.
    :raises: requests_async.RequestTimeout | requests_async.RequestException | pybusent.StopNotExist
    """
    try:
        xml = await request_wsdl_stop(stopid)

    except HTTPError as request_error:
        # When the Stop not exists, the WSDL API returns 500 causing a HTTPError
        # We use the following parser helper to check if the API returned an error because the stop not exists
        if parse_xml_error_stop_not_exist(request_error.response.text):
            raise StopNotExist()
        else:
            raise request_error

    else:
        return parse_xml_stop(xml)
