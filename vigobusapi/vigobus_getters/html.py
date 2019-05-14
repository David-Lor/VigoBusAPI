"""HTML PSEUDO-API
Functions to query to the mobile webpage, as a backup of the main WSDL API.
"""

# # Native # #
import traceback
from typing import Union, List

# # Installed # #
from requests_html import HTMLSession, HTMLResponse, HTML
from pybuses import Bus, Stop
# noinspection PyPackageRequirements
from requests.exceptions import RequestException

# # Project # #
from vigobusapi.settings_handler import load_settings

# # Package # #
from .string_fixes import fix_stop_name, fix_bus

# Settings
settings = load_settings()
HTTP_URL = settings["HTTP_REMOTE_API"]  # + stopid
HTTP_TIMEOUT = settings["HTTP_REQUEST_TIMEOUT"]  # Default timeout, can be changed when calling function

__all__ = ("stop_html", "buses_html")


def _get_html(url: str, timeout: int) -> Union[HTML, None]:
    """Performs a HTTP request to the page for the desired Stop.
    The webpage contains the stop name and the incoming buses.
    :param url: URL to get HTML from (required)
    :param timeout: Timeout for the request (required)
    :type url: str
    :type timeout: int
    :return: HTML source |
             None if some error happened
    :rtype: str or None
    """
    try:
        session = HTMLSession()
        # noinspection PyTypeChecker
        r: HTMLResponse = session.get(url, timeout=timeout)
    except RequestException:
        print(f"Error requesting/fetching source of URL '{url}':\n{traceback.format_exc()}")
        return None
    else:
        return r.html


def _get_stop_html(stopid: Union[int, str], timeout: int) -> Union[HTML, None]:
    """Performs a HTTP request to the page for the desired Stop.
    The webpage contains the stop name and the incoming buses.
    :param stopid: stop ID/Number (required)
    :param timeout: Timeout for each request (required)
    :type stopid: int or str
    :type timeout: int
    :return: HTML source |
             None if some error happened
    :rtype: str or None
    """
    url = HTTP_URL + str(stopid)
    return _get_html(url, timeout)


def buses_html(stopid: Union[int, str], timeout: int = HTTP_TIMEOUT) -> Union[List[Bus], None]:
    """Get buses from HTML. Only up to 5 buses are fetched. Stop must exist.
    :param stopid: stop ID/Number (required)
    :param timeout: Timeout for each request (default=HTTP_TIMEOUT)
    :type stopid: int or str
    :type timeout: int
    :return: list of Bus objects with name filled (empty if no buses available) |
             None if couldn't fetch info or some error happened
    :rtype: list or None
    """
    # noinspection PyBroadException
    try:
        html = _get_stop_html(stopid, timeout)
        if html is None:
            return None

        buses = list()  # If no buses found, this list will be empty
        rows_all = html.find("tr")
        rows = [
            r for r in rows_all
            if "style" in r.attrs.keys()
               and ("color:#333333;background-color:#F7F6F3;" in r.attrs["style"]
                    or "color:#284775;background-color:White;" in r.attrs["style"])
        ]

        for row in rows:
            cols = row.find("td")
            line = cols[0].text.replace(" ", "")
            route = cols[1].text.lstrip()
            time = cols[2].text
            line, route = fix_bus(line, route)
            buses.append(Bus(
                line=line,
                route=route,
                time=int(time)
            ))

    except Exception:
        print(f"Error fetching buses for Stop #{stopid} using HTML:\n{traceback.format_exc()}")
        return None  # Error happened

    else:
        return buses


def stop_html(stopid: Union[int, str], timeout: int = HTTP_TIMEOUT) -> Union[Stop, bool, None]:
    """Get Stop info from HTML. Only name can be fetched.
    :param stopid: stop ID/Number (required)
    :param timeout: Timeout for each request (default=HTTP_TIMEOUT)
    :param timeout: Timeout for each request (optional)
    :type stopid: int
    :type timeout: int
    :return: Stop object with name filled, if stop found |
             False if stop not found (reported by remote server as non-existent) |
             None if couldn't fetch info or some error happened
    :rtype: Stop or False or None
    """
    html = None
    # noinspection PyBroadException
    try:
        html = _get_stop_html(stopid, timeout)
        if html is None:
            return None

        if "Parada Inexistente" in html:
            return False  # Stop does not exist

        # noinspection PyArgumentList
        name = html.find("span", {"id": "lblNombre"}).text  # Get Stop Name
        if not name:  # Name not found
            print(f"Could not find Name for the Stop #{stopid} in HTML. HTML source obtained:\n{html}")
            return None  # Other errors

        return Stop(  # Stop found, return Stop object with Name
            stopid=int(stopid),
            name=fix_stop_name(name)
        )

    except Exception:
        print(f"Error fetching Stop #{stopid} from HTML:\n{traceback.format_exc()}\nHTML obtained:{html}")
        return None  # Other errors
