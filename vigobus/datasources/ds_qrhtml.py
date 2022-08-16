from .base import BaseDatasource, Datasources


@Datasources.register(priority=100)
class DatasourceQrHtml(BaseDatasource):
    _endpoint = ""
