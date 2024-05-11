import io
import csv
from typing import List

from vigobus.datasources.base import BaseDatasource
from vigobus.datasources.fixers import Fixers
from vigobus.models.stop import Stop, StopMetadata
from vigobus.models.base import BaseModel, PosInt, NEString, Position, SourceMetadata
from vigobus.utils import Utils


class DatasourceVigoOpenData(BaseDatasource):
    _paradas_endpoint = "https://datos.vigo.org/data/transporte/paradas.csv"

    class StopCsvLine(BaseModel):
        id: PosInt
        nombre: NEString
        lat: float
        lon: float

    async def get_all_stops(self) -> List[Stop]:
        r = await self._request_http(
            url=self._paradas_endpoint,
        )
        return list(self._parse_stops_dump_csv(r.text))

    async def get_all_stops_etag(self) -> str:
        r = await self._request_http(
            url=self._paradas_endpoint,
            method="HEAD"
        )
        return r.headers["ETag"]

    def _parse_stops_dump_csv(self, data: str):
        source_metadata = SourceMetadata(
            datasource=self.datasource_name,
            when=Utils.datetime_now(),
        )
        reader = csv.DictReader(io.StringIO(data))

        for row in reader:
            stop_original = self.StopCsvLine.parse_obj(row)
            name_original = stop_original.nombre
            name = Fixers.stop_name(name_original)

            # noinspection PyTypeChecker
            yield Stop(
                id=stop_original.id,
                name=name,
                position=Position(lat=stop_original.lat, lon=stop_original.lon),
                metadata=StopMetadata(
                    original_name=name_original,
                    source=source_metadata,
                ),
            )
