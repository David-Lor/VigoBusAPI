from .base import BaseDatasource, Datasources


@Datasources.register(priority=300)
class DatasourceQrHtml(BaseDatasource):
    _endpoint = ""
