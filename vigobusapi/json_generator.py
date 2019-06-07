"""JSON_GENERATOR
Module to generate JSON responses for endpoint requests.
"""

# # Native # #
from typing import Optional, Dict, List

# # Installed # #
from pybuses import Stop, Bus

__all__ = ("stop_to_json", "buses_to_json")


def stop_to_json(stop: Optional[Stop]) -> Dict:
    stop_exists = bool(stop)
    js = {
        "exists": stop_exists
    }
    if stop_exists:
        js["stopid"] = stop.stopid
        js["name"] = stop.name
        if stop.has_location():
            js["lat"] = stop.lat
            js["lon"] = stop.lon
    return js


def buses_to_json(buses: List[Bus], stop_exists: bool) -> Dict:
    js = {
        "exists": stop_exists
    }
    if stop_exists:
        js["buses"] = list()
        for bus in buses:
            js["buses"].append({
                "line": bus.line,
                "route": bus.route,
                "time": bus.time,
                "distance": bus.distance
            })
    return js
