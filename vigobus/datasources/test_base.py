import pytest

from .base import BaseDatasource, Datasources
from ..exceptions import DatasourceMethodUnavailableException


def teardown_function():
    Datasources.reset()


@pytest.mark.asyncio
async def test_datasources_decorator():
    """Declare 3 BaseDatasource based classes:
    - DSMiddle with no defined priority (100 by default)
    - DSLow with a priority of 1
    - DSHigh with a priority of 1000

    Call the Datasources.get_datasources() method. Should return the declared Datasources, sorted by priority,
    from higher to lower.

    Call the methods from all the datasources. Should raise the DatasourceMethodUnavailableException.
    """

    @Datasources.register
    class DSMiddle(BaseDatasource):
        pass

    @Datasources.register(priority=1)
    class DSLow(BaseDatasource):
        pass

    @Datasources.register(priority=1000)
    class DSHigh(BaseDatasource):
        pass

    expected_datasources = [DSHigh, DSMiddle, DSLow]
    datasources = Datasources.get_datasources()
    assert datasources == expected_datasources

    for datasource in datasources:
        datasource = datasource()
        with pytest.raises(DatasourceMethodUnavailableException):
            await datasource.get_stop(1)
        with pytest.raises(DatasourceMethodUnavailableException):
            await datasource.get_buses(1)
