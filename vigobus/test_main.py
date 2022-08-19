import freezegun

from . import Stop, Position, StopMetadata, SourceMetadata, Vigobus
from .datasources.base import BaseDatasource
from .conftest import TestMarks, Datetimes


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

    class DS1(BaseDatasource):
        async def get_stop(self, stop_id: int):
            raise Exception("Exception from DS1.get_stop()")

    class DS2(BaseDatasource):
        pass

    class DS3(BaseDatasource):
        async def get_stop(self, stop_id: int):
            called_datasources.append(self.datasource_name)
            return expected_response

    class DS4(BaseDatasource):
        async def get_stop(self, stop_id: int):
            called_datasources.append(self.datasource_name)
            return None

    vigobus = Vigobus(
        datasources_getstop=[DS1, DS2, DS3, DS4],
    )
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
async def test_vigobus_getstop_nonexisting_real():
    vigobus = Vigobus()
    stop_result = await vigobus.get_stop(1)
    # stop_id = 1 on DatasourceVigoApi returns a non-existing stop,
    # but with weird estimations (buses with distance_meters=-1)

    assert stop_result is None


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
