
# # Native # #
from typing import Optional, Dict

# # Installed # #
from pybuses import Stop


def stop_to_json(stop: Optional[Stop]) -> Dict:
    js = {
        "exists": bool(stop)
    }
    if js["exists"]:
        js["stopid"] = stop.stopid
        js["name"] = stop.name
        if stop.has_location():
            js["lat"] = stop.lat
            js["lon"] = stop.lon
    return js
