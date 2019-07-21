"""MONGODB DATA SOURCE
This data source is a local storage based on a MongoDB database to store Stops, so there is no need to fetch their data
from the external data source, saving bandwith and requests, and improving performance.
"""

from .mongo import *
