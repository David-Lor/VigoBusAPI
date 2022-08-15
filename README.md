# Python VigoBusAPI

[![OpenAPI docs (stable)](https://img.shields.io/badge/OpenAPI%20docs-stable-green?logo=swagger&style=plastic)](https://editor.swagger.io/?url=https://raw.githubusercontent.com/David-Lor/VigoBusAPI/master/docs/openapi.yaml)
[![OpenAPI docs (develop)](https://img.shields.io/badge/OpenAPI%20docs-develop-blue?logo=swagger&style=plastic)](https://editor.swagger.io/?url=https://raw.githubusercontent.com/David-Lor/VigoBusAPI/develop/docs/openapi.yaml)

REST API that provides Stop and Bus information provided by the public transport system of the city of [Vigo](https://en.wikipedia.org/wiki/Vigo) (Galicia/Spain). Built with Python + [FastAPI](https://github.com/tiangolo/fastapi).

The goal of this API is to gather the different available data sources on one single API,
with better endpoints structure and more clear data output format (as JSON).

## Features

## Structure

## Project structure

The VigoBusAPI project is divided in two parts:

- the vigobus library is a Python library that provides all the logic for fetching, parsing and formatting all the data supported
- the vigobusapi app is the REST API that, using the vigobus library, provides endpoints for accessing all the data supported

## Static stops

The stops' information (id, name, location...) is supposed to be static, because hardly ever change. New stops may be added, while others may be removed, but this should happen from time to time.
With this in mind, this information follows these principles:

- VigoBusAPI uses a single source of truth (SSoT): the stops branch on this repository.
- Although the stops' information come from external data sources, it has some problems and caveats that we try to solve here:
  - Fixing and normalizing names.
  - Adding external tags, to ease searches.
  - Being on GitHub, this information can be improved by the community in different ways, via issues or pull requests.
- The API server reads the stops from a MongoDB database, where the information is synched with the SSoT. The database acts as a server datasource, and allows for better fuzzy queries, like search by name (vanilla string indexes in MongoDB are pretty decent).
- If a stop is not found on the database, it is searched on an external data source, by the API server itself. *(The SSoT should be "notified" about this)
- The SSoT should be periodically synched with the external datasources, to update data from saved stops, or remove expired stops.

## [Changelog](CHANGELOG.md)

## Disclaimer

This project is not endorsed by, directly affiliated with, maintained by, sponsored by or in any way officially connected with the company or companies responsible for the public transport service of the city of Vigo.

_Este proyecto no cuenta con soporte, no está afiliado con, mantenido por, patrocinado por ni en cualquier otra manera oficialmente conectado con la compañía o compañías responsables del sistema de transporte público de la ciudad de Vigo._
