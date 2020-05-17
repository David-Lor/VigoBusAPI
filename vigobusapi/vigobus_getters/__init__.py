"""VIGOBUS GETTERS
Functions that retrieve, parse and translate the Stop/Bus data received from the external data sources.
Is recommended to use the 'get_stop'/'get_buses' functions to let them decide what getter/data source/s to use,
unless the client specifies otherwise when performing a request.
"""

from .html import get_stop as html_get_stop
from .html import get_buses as html_get_buses
from .mongo import search_stops
from .auto_getters import get_stop, get_buses
from .exceptions import ParseError
