
# # Native # #
import os
import signal
from typing import Optional, Dict

# # Installed # #
from timeout_decorator import timeout
from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer

# # Project # #
from vigobusapi.settings_handler import load_settings
from vigobusapi.vigobus_getters import *

settings = load_settings()
ENDPOINT_TIMEOUT = settings["ENDPOINT_TIMEOUT"]
API_STOP_TIMEOUT = settings["API_STOP_TIMEOUT"]
HOST = settings["API_HOST"]
PORT = settings["API_PORT"]
FLASK_NAME = settings["API_NAME"]
DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(FLASK_NAME)


def __generate_response(
        js: Optional[Dict] = None,
        text: Optional[str] = None,
        status: int = 200,
        mimetype: str = "application/json"
):
    return Response(
        response=text if text and not js else str(js).replace("'", '"'),
        status=status,
        mimetype=mimetype,
        content_type=f"{mimetype}; charset=utf-8",
    )


def __process_params(req: request) -> dict:
    """Process the parameters of a Request
    :param req: flask request
    :type req: flask.request
    :return: dict
    """
    return {
        "source": req.args.get("source")  # wsdl or html
    }


# @app.route("/proxies")
# def __publicip():
#     proxies = get_all_proxies()
#     s = "<h1>Found {} proxies</h1>".format(len(proxies))
#     if None not in proxies:
#         proxies.append(None)
#     s += "\n" + str(proxies)
#     for proxy in proxies:
#         session = requests_html.HTMLSession()
#         session.proxies = {"http": proxy, "https": proxy}
#         s += "\n<h2>{}) {} - ".format(
#             proxies.index(proxy) + 1,
#             proxy
#         )
#         try:
#             r = session.get("https://api.ipify.org/?format=raw", timeout=3)
#             rout = r.text
#         except (RequestException, HTTPError, ProxySchemeUnknown):
#             s += "Error:</h2>\n<p>{}</p>".format(traceback.format_exc())
#         else:
#             s += "Public IP: {}".format(rout)
#     return __generate_response(text=s, mimetype="text/text")


@app.route("/stop/<stopid>")
@timeout(ENDPOINT_TIMEOUT)
def __stop(stopid):
    params = __process_params(request)
    stop_getter = get_stop_html if params.get("source") == "html" else get_stop
    stop = stop_getter(stopid)
    code = 200

    if stop is None:
        js = {
            "error": 1
        }
        code = 500

    elif stop is False:
        js = {
            "error": 0,
            "exists": 0
        }

    else:
        js = {
            "error": 0,
            "exists": 1,
            "name": stop.name,
            "lat": stop.lat,
            "lon": stop.lon
        }

    return __generate_response(js=js, status=code)


@app.route("/buses/<stopid>")
@timeout(ENDPOINT_TIMEOUT)
def __buses(stopid):
    params = __process_params(request)
    buses_getter = get_buses_html if params.get("source") == "html" else get_buses
    buses = buses_getter(stopid=stopid)
    code = 200

    if buses is None:
        js = {
            "error": 1
        }
        code = 500

    else:
        mybuses = list()
        for bus in buses:
            mybuses.append({
                "line": bus.line,
                "route": bus.route,
                "dist": bus.distance if isinstance(bus.distance, int) else -1,
                "time": bus.time,
            })
        js = {
            "error": 0,
            "buses": mybuses
        }

    return __generate_response(js=js, status=code)


@app.route("/nearstops/<lat>/<lon>")
@timeout(ENDPOINT_TIMEOUT)
def __nearstops(lat, lon):
    stops = get_near_stops(float(lat), float(lon))
    code = 200

    if stops is None:
        js = {
            "error": 1
        }
        code = 500

    else:
        detailed_stops = list()
        for stop in stops:
            detailed_stops.append({
                "id": stop.stopid,
                "name": stop.name,
                "lat": stop.lat,
                "lon": stop.lon,
                "distance": stop.other["distance"]
            })
        js = {
            "error": 0,
            "stops_ids": [s.stopid for s in stops],
            "stops": detailed_stops
        }

    return __generate_response(js=js, status=code)


def run(host=HOST, port=PORT):
    http_server = WSGIServer((host, port), app)

    # noinspection PyUnusedLocal
    def signal_handler(signum, frame):
        print("Stopping server...")
        http_server.stop(timeout=API_STOP_TIMEOUT)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print(f"Server started on {host}:{port}!")
    http_server.serve_forever()
    print("Server stopped!")


if __name__ == '__main__':
    run()
