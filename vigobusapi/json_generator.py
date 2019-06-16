"""JSON_GENERATOR
Module to generate JSON responses for endpoint requests.
"""

# # Native # #
from typing import Optional, Dict, List

# # Installed # #
from pybuses_entities import Stop, Bus

__all__ = ("stop_to_json", "buses_to_json")


def stop_to_json(stop: Optional[Stop]) -> Dict:
    stop_exists = bool(stop)
    js = {
        "exists": stop_exists
    }
    if stop_exists:
        js.update(stop.get_dict())
    return js


def buses_to_json(buses: List[Bus], stop_exists: bool) -> Dict:
    js = {
        "exists": stop_exists
    }
    if stop_exists:
        js["buses"] = list()
        for bus in buses:
            js["buses"].append(bus.get_dict())
    return js
