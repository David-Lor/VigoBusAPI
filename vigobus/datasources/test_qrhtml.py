import zipfile
import freezegun

import httpx
import pydantic
import pytest

from .ds_qrhtml import DatasourceQrHtml
from .. import Stop, StopMetadata, SourceMetadata
from ..conftest import TestMarks, Datetimes


class MockDatasourceQrHtml(DatasourceQrHtml):
    _mocked_response: httpx.Response = pydantic.PrivateAttr()

    def set_response(self, status_code: int, content, **kwargs):
        self._mocked_response = httpx.Response(
            status_code=status_code,
            content=content,
            **kwargs,
        )

    async def _request_http(self, url: str, raise_status: bool = True, **kwargs) -> httpx.Response:
        return self._mocked_response


# noinspection PyTypeChecker
@TestMarks.asyncio
@pytest.mark.parametrize("html_filename, stop_id, expected_result", [
    ("datasource_qrhtml_5800_buses_page1.html", 5800, Stop(
        id=5800,
        name="Rúa de Jenaro de la Fuente, 29",
        position=None,
        metadata=StopMetadata(
            original_name="Rúa de Jenaro de la Fuente, 29",
            source=SourceMetadata(
                datasource="MockDatasourceQrHtml",
                when=Datetimes[-1],
            ),
        ),
    )),
    ("datasource_qrhtml_6420_nobuses.html", 6420, Stop(
        id=6420,
        name="Paseo de Alfonso XII (Mirador)",
        position=None,
        metadata=StopMetadata(
            original_name="Paseo de Alfonso XII (Mirador)",
            source=SourceMetadata(
                datasource="MockDatasourceQrHtml",
                when=Datetimes[-1],
            ),
        ),
    )),
    ("datasource_qrhtml_nonexisting.html", 1234, None),
])
async def test_qrhtml_getstop_mockhtml(testdata: zipfile.ZipFile, html_filename, stop_id, expected_result):
    generation_datetime = expected_result.metadata.source.when if expected_result else Datetimes[0]

    ds = MockDatasourceQrHtml()
    html_response = testdata.open(html_filename).read()
    ds.set_response(200, html_response)

    with freezegun.freeze_time(generation_datetime):
        result = await ds.get_stop(stop_id)

    assert result == expected_result
