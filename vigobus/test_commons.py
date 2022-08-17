import datetime

import pytest


class TestMarks:
    real = pytest.mark.real
    heavy = pytest.mark.heavy
    asyncio = pytest.mark.asyncio


Datetimes = [
    datetime.datetime(2022, 10, 1, 16, 20, tzinfo=datetime.timezone.utc),
    datetime.datetime(2022, 10, 2, 10, tzinfo=datetime.timezone.utc),
]
