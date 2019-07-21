"""ENTITIES
Custom classes to be used as data entities
"""

# # Native # #
import datetime
import copy

# # Typing # #
from typing import Optional

# # Installed # #
from pybusent import AdvancedStop

__all__ = ("Stop", "OptionalStop")


class Stop(AdvancedStop):
    """Custom Stop entity inherited from pybusent.AdvancedStop.
    Required to add special fields and special format/parsing to write on and read from MongoDB.
    """
    created: Optional[datetime.datetime]

    def __init__(self, **kwargs):
        # From Mongo to Python
        # Translate _id to stopid
        try:
            kwargs["stopid"] = kwargs.pop("_id")
        except KeyError:
            # Raise the exception on the super entity Init (stopid is always required)
            pass
        super(Stop, self).__init__(**kwargs)

    def get_mongo_dict(self):
        """Same as get_dict, but rename the 'stopid' key to '_id', to use it as the ID of the document.
        Call this method instead of 'get_dict' to save the stop in MongoDB.
        """
        # From Python to Mongo
        # Translate stopid to _id
        d = copy.deepcopy(super(Stop, self).get_dict())
        d["_id"] = d.pop("stopid")
        # Remove source field
        d.pop("source")
        return d


OptionalStop = Optional[Stop]
