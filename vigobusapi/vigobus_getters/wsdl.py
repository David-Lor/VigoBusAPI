"""WSDL API
Functions to query the official WSDL API.
"""

# # Native # #
import traceback
from typing import List, Union

# # Installed # #
import zeep  # WSDL client - http://docs.python-zeep.org/en/master/
from bs4 import BeautifulSoup  # XMLParser
from pybuses import Bus, Stop

# # Project # #
from vigobusapi.settings_handler import load_settings

# # Package # #
from .string_fixes import fix_stop_name, fix_bus


settings = load_settings()
WSDL_URL = settings["WSDL_REMOTE_API"]
WSDL_TIMEOUT = settings["WSDL_REQUEST_TIMEOUT"]  # Timeout for WSDL (timeout & operation_timeout)

__all__ = ("stop_wsdl", "buses_wsdl", "near_stops_wsdl")


# def _get_wsdl_client(proxy=True) -> zeep.Client:
#     """Generate a zeep.Client object with or without a proxy.
#     The proxy will be fetched randomly if proxy=True, otherwise no proxy will be used.
#     :param proxy: True to use a proxy, False to connect without proxy (optional, default=True)
#     :type proxy: bool
#     :return: zeep.Client object
#     :rtype: zeep.Client
#     """
#     transport = zeep.Transport(timeout=WSDL_TIMEOUT*2, operation_timeout=WSDL_TIMEOUT)
#     if proxy:
#         # transport.session.proxies = {"http":get_proxy()}
#         myproxy = get_random_proxy()
#         if myproxy:
#             transport.session.proxies = {"http": myproxy, "https": myproxy}
#     return zeep.Client(wsdl=WSDL_URL, transport=transport)


def _get_wsdl_client(timeout: int) -> zeep.Client:
    """Generate a zeep.Client.
    :return: zeep.Client object
    :rtype: zeep.Client
    """
    transport = zeep.Transport(timeout=timeout, operation_timeout=timeout)
    return zeep.Client(wsdl=WSDL_URL, transport=transport)


def _xml_to_buses(xml_buses) -> List[Bus]:
    """Convert a XML list of buses to a list of Bus objects.
    :param xml_buses: raw XML list of buses (required)
    :type xml_buses: bs4.ResultSet
    :return: List of Bus objects
    :rtype: List[Bus]
    """
    buses = list()

    for xml in xml_buses:
        line = xml.find("linea").text
        route = xml.find("ruta").text
        time = int(xml.find("minutos").text)
        distance = int(xml.find("metros").text)

        line, route = fix_bus(line, route)
        buses.append(Bus(
            line=line,
            route=route,
            time=time,
            distance=distance
        ))

    return buses


def stop_wsdl(stopid, timeout: int = WSDL_TIMEOUT) -> Union[Stop, bool, None]:
    """Search a Stop using WSDL.
    :param stopid: StopID to search (required)
    :param timeout: WSDL timeout (default=WSDL_TIMEOUT variable)
    :type stopid: int
    :type timeout: int
    :return: Stop object with id, name and position filled, if stop was found |
             False if stop not found |
             None if some technical error happened
    :rtype: Stop or bool or None
    """
    try:
        client = _get_wsdl_client(timeout)
        xml_raw = client.service.BuscarParadasIdParada(stopid)
        xml = BeautifulSoup(xml_raw, "lxml").find("parada")
        name = fix_stop_name(xml["nombre"])
        lat = xml.get("latitud")
        lon = xml.get("longitud")

    except Exception as ex:  # Stop not found or error happened
        if "No hay ninguna fila en la posición" in str(ex):
            return False  # Stop not found/does not exist
        else:
            print(f"Error geting info for Stop #{stopid} from WSDL:"
                  f"\n{traceback.format_exc()}")
            return None  # Error happened

    else:  # Stop found
        return Stop(
            stopid=stopid,
            name=name,
            lat=lat,
            lon=lon
        )


def buses_wsdl(stopid, timeout: int = WSDL_TIMEOUT) -> Union[List[Bus], None]:
    """Search the buses coming to a stop using WSDL.
    :param stopid: StopID to search incoming buses (required)
    :param timeout: WSDL timeout (default=WSDL_TIMEOUT variable)
    :type stopid: int
    :type timeout: int
    :return: list of Bus objects, empty list if no buses available |
             None if some technical error happened
    :rtype: list or None
    """
    # noinspection PyBroadException
    try:
        client = _get_wsdl_client(timeout)
        xml_raw = client.service.EstimacionParadaIdParada(stopid)
        xml_buses = BeautifulSoup(xml_raw, "lxml").find_all("estimaciones")
        buses = _xml_to_buses(xml_buses)

    except Exception:
        print(f"Error getting buses for Stop #{stopid} from WSDL:\n{traceback.format_exc()}")
        return None

    else:
        return buses


def near_stops_wsdl(lat, lon, timeout: int = WSDL_TIMEOUT) -> Union[List[Stop], None]:
    """Search the stops near a certain location (using coordinates) using WSDL.
    :param lat: Latitude (required)
    :param lon: Longitude (required)
    :param timeout: WSDL timeout (default=WSDL_TIMEOUT variable)
    :type lat: float
    :type lon: float
    :type timeout: int
    :return: list of Stop objects or empty list |
             None if some technical error happened
    :rtype: list or None
    """
    # noinspection PyBroadException
    try:
        client = _get_wsdl_client(timeout)
        xml_raw = client.service.BuscarParadas(lat, lon)
        xml_stops = BeautifulSoup(xml_raw, "lxml").find_all("parada")
        stops = list()
        for dict_stop in xml_stops:
            stops.append(Stop(
                stopid=dict_stop["idparada"],
                name=dict_stop["nombre"],
                lat=dict_stop["latitud"],
                lon=dict_stop["longitud"],
                other={"distance": float(dict_stop["distancia"])}
            ))

    except Exception:
        print(f"Error getting near stops from WSDL:\n{traceback.format_exc()}")
        return None

    else:
        return stops
