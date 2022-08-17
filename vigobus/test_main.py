import freezegun

from . import Stop, Position, StopMetadata, SourceMetadata
from .main import Vigobus
from .datasources.base import BaseDatasource, Datasources
from .test_commons import TestMarks, Datetimes


def teardown_function():
    Datasources.reset()


# noinspection PyUnusedLocal
@TestMarks.asyncio
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


@TestMarks.real
@TestMarks.asyncio
async def test_vigobus_getstop_real():
    stop_id = 5800
    stop_generation_datetime = Datetimes[0]
    # noinspection PyTypeChecker
    stop_expected = Stop(
        id=stop_id,
        name="Rúa de Jenaro de la Fuente 29",
        position=Position(lat=42.232202275, lon=-8.703792246),
        metadata=StopMetadata(
            original_name="Rúa de Jenaro de la Fuente  29",
            source=SourceMetadata(
                datasource="DatasourceVigoApi",
                when=stop_generation_datetime,
            ),
        ),
    )

    vigobus = Vigobus()

    with freezegun.freeze_time(stop_generation_datetime):
        stop_result = await vigobus.get_stop(stop_id)

    assert stop_result == stop_expected


@TestMarks.real
@TestMarks.asyncio
async def test_vigobus_getallstops_real():
    stops_generation_datetime = Datetimes[0]
    # noinspection PyTypeChecker
    stops_expected_first = Stop(
        id=6930,
        name="Praza de América 1",
        position=Position(lat=42.220997313, lon=-8.732835177),
        metadata=StopMetadata(
            original_name="Praza de América  1",
            source=SourceMetadata(
                datasource="DatasourceVigoOpenData",
                when=stops_generation_datetime,
            )
        )
    )

    vigobus = Vigobus()

    with freezegun.freeze_time(stops_generation_datetime):
        stops_result = await vigobus.get_all_stops()

    assert len(stops_result) > 1100
    assert stops_result[0] == stops_expected_first


@TestMarks.real
@TestMarks.heavy
@TestMarks.asyncio
async def test_vigobus_getallstops_real_compare_getstop():
    vigobus = Vigobus()
    stops = await vigobus.get_all_stops()
    stop_dict_exclude_fields = {"metadata"}

    for stop_getallstops in stops:
        stop_getonestop = await vigobus.get_stop(stop_getallstops.id)
        assert stop_getonestop.dict(exclude=stop_dict_exclude_fields) == \
               stop_getallstops.dict(exclude=stop_dict_exclude_fields)
