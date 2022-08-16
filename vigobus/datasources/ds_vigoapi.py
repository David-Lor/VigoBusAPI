from .base import BaseDatasource, Datasources


@Datasources.register(priority=1000)
class DatasourceVigoAPI(BaseDatasource):
    pass
