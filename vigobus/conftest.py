import datetime

import pytest

from . import Vigobus
from .datasources.base import Datasources


class TestMarks:
    real = pytest.mark.real
    heavy = pytest.mark.heavy
    asyncio = pytest.mark.asyncio


Datetimes = [
    datetime.datetime(2022, 10, 1, 16, 20, tzinfo=datetime.timezone.utc),
    datetime.datetime(2022, 10, 2, 10, tzinfo=datetime.timezone.utc),
]


class VigobusUnit(Vigobus):
    def __init__(self, **data):
        super().__init__(**data)
        self._datasources.clear()

    def reload(self):
        self._initialize_datasources()


@pytest.yield_fixture
def vigobus_real() -> Vigobus:
    # TODO Real tests failing when running all, after running the unit like tests
    #  (seems they still load the testing datasources from previous tests)
    Datasources.reset()
    instance = Vigobus()
    yield instance
    Datasources.reset()


@pytest.yield_fixture
def vigobus_unit() -> VigobusUnit:
    Datasources.reset()
    instance = VigobusUnit()
    yield instance
    Datasources.reset()
