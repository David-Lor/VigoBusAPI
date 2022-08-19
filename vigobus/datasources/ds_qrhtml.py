from typing import Optional

import bs4
import httpx

from .base import BaseDatasource
from .fixers import Fixers
from .. import Stop, BusesResponse, StopMetadata, SourceMetadata
from ..utils import Utils


class DatasourceQrHtml(BaseDatasource):
    URL = "http://infobus.vitrasa.es:8002/Default.aspx"
    HEADERS = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-encoding': 'accept-encoding',
        'accept-language': 'es,en-US;q=0.7,en;q=0.3',
        'dnt': '1',
        'connection': 'keep-alive',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'
    }
    BS4_PARSER = "lxml"

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        r = await self._request(stop_id)
        soup = bs4.BeautifulSoup(r.text, self.BS4_PARSER)
        return self._parse_response_stop(soup)

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        pass

    async def _request(self, stop_id: int) -> httpx.Response:
        params = {"parada": stop_id}
        headers = {**self.HEADERS}

        return await self._request_http(
            url=self.URL,
            params=params,
            headers=headers,
        )

    @classmethod
    def _parse_stop_exists(cls, body: str) -> bool:
        return "Parada Inexistente" not in body

    def _parse_response_stop(self, soup: bs4.BeautifulSoup) -> Optional[Stop]:
        if not self._parse_stop_exists(soup.text):
            return None

        now = Utils.datetime_now()
        stop_id = soup.find("span", id="lblParada").text
        stop_name_original = soup.find("span", id="lblNombre").text
        stop_name = Fixers.stop_name(stop_name_original)

        # noinspection PyTypeChecker
        return Stop(
            id=stop_id,
            name=stop_name,
            position=None,
            metadata=StopMetadata(
                original_name=stop_name_original,
                source=SourceMetadata(
                    datasource=self.datasource_name,
                    when=now,
                ),
            ),
        )

    def _parse_response_buses(self, soup: bs4.BeautifulSoup) -> BusesResponse:
        pass
