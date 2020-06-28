"""TEST - Get Stop
Get a Stop from the API
"""

# # Native # #
import asyncio

# # Installed # #
import requests
from fastapi import status as statuscode

# # Project # #
from vigobusapi.entities import Stop
from vigobusapi.vigobus_getters.mongo.mongo_write import insert_stops

# # Package # #
from .base_test import *

EXISTING_STOP = 5800
EXISTING_STOP_NAME = "Jenaro de la Fuente, 33"
NONEXISTING_STOPS = [0, 1, 2, 3, 4]


class TestGetStop(BaseTest):
    def request(self, stop_id: int, status: int = statuscode.HTTP_200_OK):
        r = requests.get(f"{self.api_url}/stop/{stop_id}")
        assert r.status_code == status
        return r

    def test_get_stop_from_external(self):
        """Get a Stop. It should return it from HTML data source, with the expected name.
        Then get it again. It should return it from cache data source"""
        stop_id = EXISTING_STOP

        response_1 = self.request(stop_id)
        response_stop_1 = Stop(**response_1.json())
        assert response_stop_1.stop_id == stop_id
        assert response_stop_1.source == "html"
        assert response_stop_1.name == EXISTING_STOP_NAME

        response_2 = self.request(stop_id)
        response_stop_2 = Stop(**response_2.json())
        assert response_stop_2.stop_id == stop_id
        assert response_stop_2.source == "stop_cache"
        assert {**response_stop_2.dict(), "source": ""} == {**response_stop_1.dict(), "source": ""}

    def test_get_nonexisting_stop_from_external(self):
        """Get a Stop that does not exist. It should return 404"""
        self.request(NONEXISTING_STOPS.pop(), status=statuscode.HTTP_404_NOT_FOUND)

    def test_get_stop_from_mongo(self):
        """Having a (nonexisting in real world) Stop in Mongo, get it.
        Should return it from mongo data source"""
        stop = Stop(stop_id=NONEXISTING_STOPS.pop(), name="fake stop", lat=1.234, lon=4.321, source="html")
        stop_fields = {"stop_id", "name", "lat", "lon"}

        save_stop_coro = insert_stops(stop)
        asyncio.get_event_loop().run_until_complete(save_stop_coro)

        response = self.request(stop.stop_id)
        response_stop = Stop(**response.json())

        assert response_stop.source == "mongo"
        assert response_stop.dict(include=stop_fields) == stop.dict(include=stop_fields)
