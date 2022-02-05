# Changelog

## 0.9.0

- fix getting reduced buses list from cache was returning 'no more buses available' flag
- fix different buses lists being returned when getting reduced vs completed list (HTTP datasource)
- export OpenAPI schemas (json/yaml) with Github Actions workflow
- modify search stops endpoint for getting multiple stops by id in single request
- add alias path to Get Buses endpoint
- fix correct initialization of single Motor mongodb client
- upgrade requirements versions
- _reparado problema al obtener buses desde cache, devolviendo 'no more buses available'_
- _reparado problema al obtener buses desde fuente de datos HTTP, devolviendo distintos listados según se pidiese un listado parcial o completo_
- _exportación de esquemas OpenAPI (json/yaml) mediante workflow de Github Actions_
- _modificado endpoint de buscar paradas para poder buscar varias paradas por id en una única petición_
- _añadido alias para ruta de endpoint Get Buses_
- _reparada inicialización del cliente mongodb Motor, iniciando una única instancia_
- _actualizadas versiones de dependencias_

## 0.8.0

- add new online data source for buses (HTTP API)
- dotenv settings refactor
- _añadida nueva fuente de datos online para buses (HTTP API)_
- _refactorización de configuraciones .env_

## 0.7.1

- set Mongo stop name text index language to spanish
- _establecimiento de idioma spanish en text index de paradas guardadas en Mongo_

## 0.7.0

- add limit query param to search stops endpoint
- _añadida query param para limitar resultados en endpoint de buscar paradas por nombre_

## 0.6.1

- add unit tests
- fix clear_duplicated_buses function by simplifying logic
- _añadidos tests unitarios_
- _reparada función clear_duplicated_buses simplificando lógica_

## 0.6.0

- add endpoint to search stops by name
- get buses extra pages asynchronously (HTML datasource)
- _añadido endpoint para buscar paradas por nombre_
- _lectura de páginas extra de buses asíncronamente (fuente de datos HTML)_


## 0.5.0

- refactor request & error handling, imports & cache
- add logging
- _refactorización de request y error handling, imports y cache_
- _añadido sistema de logs_

## 0.4.0

- remove WSDL data sources
- _eliminada fuente de datos WSDL_

## 0.3.3

- remove dotenv-settings-handler as dependency and use pydantic only
- remove not required settings
- freeze requirements versions
- _quitada la dependencia dotenv-settings-handler y usar sólo pydantic_
- _borradas configuraciones no necesarias_
- _congeladas versiones de requirements_

## 0.3.2

- fix buses endpoint returning null source
- remove setup.py
- _reparado endpoint buses devolviendo source null_
- _borrar setup.py_

## 0.3.1

- store StopNotExist status on local Stop cache
- _guardar estado StopNotExist en caché local de Stops_

## 0.3.0

- define data models on project (deprecate pybusent)
- _definición de modelos de datos en proyecto (dejar de usar pybusent)_

## 0.2.2

- fix cache bus getter, was returning full list of buses when requesting a minimal list but a full list was cached
- _reparado cache bus getter, devolvía listado completo de buses cuando se pedía un listado parcial pero uno completo estaba almacenado_

## 0.2.1

- fix Stops endpoint, return empty array if no buses available
- _reparado endpoint Stops, devolver array vacío si no hay autobuses disponibles_

## 0.2.0

- migrated to FastAPI, new features, using MongoDB as local storage
- _migración a FastAPI, nuevas características, usando MongoDB como almacenamiento local_

## 0.1.0

- initial release
- _release inicial_
