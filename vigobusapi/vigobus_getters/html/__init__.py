"""HTML DATA SOURCE
This data source come from the mobile web available on the QR codes on the Stops.
The webpage returns up to 5 buses per page, so the Bus Getter can be requested for only the first page or all the pages.
The Stop Getter only returns the stop name.
"""

from .html import *
