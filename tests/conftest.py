import zipfile
import pathlib
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


@pytest.fixture()
def testdata() -> zipfile.ZipFile:
    this_path = pathlib.Path(__file__).parent.resolve()
    zip_path = this_path / "tests_data" / "testdata.zip"
    with zipfile.ZipFile(zip_path, "r") as f:
        yield f
