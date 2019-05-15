# Python_VigoBusAPI

Intermediate Python + Flask API that provide Stop and Bus information provided by the public transport system of the city of Vigo (Galicia/Spain).

The goal of this API is to keep the different data sources and APIs available on one single API with better endpoints structure and more clear data output format (as JSON).

## Requirements

- Python 3.7
- Docker recommended - can be deployed using the [Docker Python Autoclonable App](https://github.com/David-Lor/Docker-Python-Autoclonable-App)
- The packages listed on [requirements.txt](requirements.txt)

## Endpoints

- `/stop/<stopid>` : Get information about a Stop (name, location), given the Stop ID
- `/buses/<stopid>` : Get the Buses that will arrive to a Stop, given the Stop ID
- `/nearstops/<lat>/<lon>` : Get the Stops available near the given location, given the latitude and longitude

## Changelog

- 0.1.0 - Initial release

## TODO

- Add experimental MQTT API endpoints
- Add static route information endpoints
- Add tests (at least for String Fixing)

## Disclaimer

This project is not endorsed by, directly affiliated with, maintained, sponsored, endorsed by or in any way officially connected with the company or companies responsible for the public transport service of the city of Vigo.
