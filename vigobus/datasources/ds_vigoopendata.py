import io
import csv
from typing import List

from .base import BaseDatasource, Datasources
from .fixers import Fixers
from .. import Stop, StopMetadata
from ..models.base import BaseModel, PosInt, NEString, Position, SourceMetadata
from ..utils import Utils


@Datasources.register(priority=100)
class DatasourceVigoOpenData(BaseDatasource):

    class StopCsvLine(BaseModel):
        id: PosInt
        nombre: NEString
        lat: float
        lon: float

    async def get_all_stops(self) -> List[Stop]:
        r = await self._request_http(
            url="https://datos.vigo.org/data/transporte/paradas.csv",
        )
        return self._parse_stops_dump_csv(r.text)

    def _parse_stops_dump_csv(self, data: str) -> List[Stop]:
        source_metadata = SourceMetadata(
            datasource=self.datasource_name,
            when=Utils.datetime_now(),
        )
        reader = csv.DictReader(io.StringIO(data))
        results: List[Stop] = list()

        for row in reader:
            stop_original = self.StopCsvLine.parse_obj(row)
            name_original = stop_original.nombre
            name = Fixers.stop_name(name_original)

            # noinspection PyTypeChecker
            results.append(Stop(
                id=stop_original.id,
                name=name,
                position=Position(lat=stop_original.lat, lon=stop_original.lon),
                metadata=StopMetadata(
                    original_name=name_original,
                    source=source_metadata,
                ),
            ))

        return results
