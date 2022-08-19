from typing import Optional, List

import bs4
import httpx

from .base import BaseDatasource
from .fixers import Fixers
from ..models import Bus, BusMetadata
from ..models import Stop, BusesResponse, StopMetadata, SourceMetadata
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
        r = await self._request(stop_id)
        soup = bs4.BeautifulSoup(r.text, self.BS4_PARSER)
        buses = self._parse_response_buses(soup)
        return BusesResponse(
            buses=buses,
            more_buses_available=False,
        )

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

    def _parse_response_buses(self, soup: bs4.BeautifulSoup) -> List[Bus]:
        buses: List[Bus] = list()
        buses_table = soup.find("table", id="GridView1")
        if not buses_table:
            return buses

        now = Utils.datetime_now()
        buses_rows_styles = (
            "color:#333333;background-color:#F7F6F3;",
            "color:#284775;background-color:White;"
        )
        buses_rows = (buses_table.find_all("tr", attrs={"style": style}) for style in buses_rows_styles)
        buses_rows = Utils.flatten(buses_rows, return_as=tuple)

        for row in buses_rows:
            column_line, column_route, column_minutes = row.find_all("td")
            bus_line_original = column_line.text
            bus_route_original = column_route.text
            bus_line, bus_route = Fixers.bus_line_route(bus_line_original, bus_route_original)

            # noinspection PyTypeChecker
            bus = Bus(
                line=bus_line,
                route=bus_route,
                time_minutes=column_minutes.text,
                distance_meters=None,
                metadata=BusMetadata(
                    original_line=bus_line_original,
                    original_route=bus_route_original,
                    source=SourceMetadata(
                        datasource=self.datasource_name,
                        when=now,
                    ),
                ),
            )
            buses.append(bus)

        return buses
