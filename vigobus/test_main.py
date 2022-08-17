import pytest

from .main import Vigobus
from .datasources.base import BaseDatasource, Datasources


def teardown_function():
    Datasources.reset()


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_vigobus_getstop_retry_datasources():
    """Test the Vigobus.get_stop() method, having 4 Datasources defined, with the following order by priority:

    - DS1: returns an exception on the method
    - DS2: has not implemented the method
    - DS3: returns OK from the method
    - DS4: returns OK from the method, but different data; this should never be reached

    The Vigobus.get_stop() method should return the response from DS3.
    The method from DS3 should be called, but not the method from DS4.
    """

    expected_response = "Response"
    called_datasources = list()

    @Datasources.register(priority=4000000)
    class DS1(BaseDatasource):
        async def get_stop(self, stop_id: int):
            raise Exception("Exception from DS1.get_stop()")

    @Datasources.register(priority=3000000)
    class DS2(BaseDatasource):
        pass

    @Datasources.register(priority=2000000)
    class DS3(BaseDatasource):
        async def get_stop(self, stop_id: int):
            called_datasources.append(self.datasource_name)
            return expected_response

    @Datasources.register(priority=1000000)
    class DS4(BaseDatasource):
        async def get_stop(self, stop_id: int):
            called_datasources.append(self.datasource_name)
            return None

    vigobus = Vigobus()
    response = await vigobus.get_stop(1)

    assert response == expected_response
    assert called_datasources == ["DS3"]
