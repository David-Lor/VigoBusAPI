"""WSDL DATA SOURCE
This data source is a WSDL/SOAP API with endpoints to retrieve Stop info, Buses and Stops near a given Location.
The Stop Getter can return the name and full location (latitude, longitude) of the Stop.
The Bus Getter is unavailable, but would return a FULL list of buses.
The NearStops Getter return the same stop information as the Stop Getter, for the Stops found near the location.
"""

from .wsdl import *
