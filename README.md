# Python VigoBusAPI

[![OpenAPI docs (stable)](https://img.shields.io/badge/OpenAPI%20docs-stable-green?logo=swagger&style=plastic)](https://editor.swagger.io/?url=https://raw.githubusercontent.com/David-Lor/VigoBusAPI/master/docs/openapi.yaml)
[![OpenAPI docs (develop)](https://img.shields.io/badge/OpenAPI%20docs-develop-blue?logo=swagger&style=plastic)](https://editor.swagger.io/?url=https://raw.githubusercontent.com/David-Lor/VigoBusAPI/develop/docs/openapi.yaml)

Intermediate Python + FastAPI API that provide Stop and Bus information provided by the public transport system of the city of Vigo (Galicia/Spain).

The goal of this API is to keep the different data sources and APIs available on one single API with better endpoints structure and more clear data output format (as JSON).

The API can output Stop information and real-time lists of Buses coming to a certain Stop, with their remaining time in minutes.

---

_API intermedia basada en Python + FastAPI que provee información de Paradas y Autobuses para el sistema de transporte público de la ciudad de Vigo (Galicia/España)._

_El objetivo de esta API es unificar las diferentes fuentes de datos y APIs disponibles en una sóla API con mejor estructura de endpoints y una salida de datos con un formato más claro (como JSON)._

_La API puede devolver información de Paradas y listados en tiempo real de los Autobuses que pasarán por una Parada concreta, con su tiempo restante en minutos._

## Features

- API powered by FastAPI, offering a REST API focused web server, fully async and auto-generating documentation.
- Nice-looking, human-readable & easily-parseable endpoint response output as JSON, compared with original data sources.
- Local data storages: Stop cache, Stop MongoDB, Buses cache; to reduce requests to the external API/data sources.
- Original API/data source fixes in Stop names and Buses lines/routes.
- Environment variables / DotEnv file - based settings system.

---

- _API basada en FastAPI, que ofrece un servidor web orientado a API REST, asíncrono y que auto-genera documentación._
- _Respuestas formateadas como JSON, con mejor estructura, legibles, coherentes y fácilmente procesables, en comparación con los resultados de las fuentes originales._
- _Sistemas de almacenamiento local: caché de Paradas, base de datos MongoDB de Paradas, caché de Autobuses; para así reducir las peticiones a las API/fuentes de datos externas._
- _Arreglo de nombres de Paradas y líneas/rutas de Autobuses en los datos devueltos por las API/fuentes de datos originales._
- _Sistema de configuración basado en variables de entorno / archivo DotEnv._

## Requirements

- Python >= 3.6
- Docker recommended - can be deployed using the [Docker Python Autoclonable App](https://github.com/David-Lor/Docker-Python-Autoclonable-App)
- The packages listed on [requirements.txt](requirements.txt)
- A MongoDB server

---

- _Python >= 3.6_
- _Docker recomendado - puede desplegarse con la imagen [Docker Python Autoclonable App](https://github.com/David-Lor/Docker-Python-Autoclonable-App)_
- _Las dependencias listadas en [requirements.txt](requirements.txt)_
- _Un servidor MongoDB_

## Endpoints

- `/stop/<stop_id>` : Get information about a Stop (name, location), given the Stop ID / _Obtener información de una Parada (nombre, ubicación), dado un código de parada_
- `/buses/<stop_id>` / `/stop/<stop_id>/buses` : Get the Buses that will arrive to a Stop, given the Stop ID / _Obtener los Autobuses que pasarán por una Parada, dado su código de parada_
- `/stops?stop_name=<name>&limit=<limit>` : Search stops by name (optional limit) / _Buscar paradas por nombre (límite opcional)_
- `/stops?stop_id=<id2>&stop_id=<id2>` : Search multiple stops by id in the same request
- `/docs` : Swagger UI (documentation) auto-generated by FastAPI / _Documentación Swagger UI auto-generada por FastAPI_

## [Changelog](CHANGELOG.md)

## TODO

- Improve Swagger/OpenAPI documentation
- Add static route information endpoints
- Add Near Stops endpoint
- Add endpoint for static maps and StreetView acquisition
- Add endpoints for static buses info
- Add integration tests
- Add detailed install & configuration instructions

---

- _Mejorar la documentación de Swagger/OpenAPI_
- _Añadir endpoint para consulta de rutas estáticas_
- _Añadir endpoint para consulta de paradas cercanas a ubicación_
- _Añadir endpoint para obtención de mapas estáticos y StreetView_
- _Añadir endpoints para consulta de información estática de buses_
- _Añadir tests de integración_
- _Añadir instrucciones detalladas de instalación y configuración_

## Disclaimer

This project is not endorsed by, directly affiliated with, maintained by, sponsored by or in any way officially connected with the company or companies responsible for the public transport service of the city of Vigo.

---

_Este proyecto no cuenta con soporte, no está afiliado con, mantenido por, patrocinado por ni en cualquier otra manera oficialmente conectado con la compañía o compañías responsables del sistema de transporte público de la ciudad de Vigo._
