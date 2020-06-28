"""BASE TEST
Definition of BaseTest class, inherited on all the system_integration tests.
It initializes the API on a Process
"""

# # Native # #
import asyncio
from multiprocessing import Process

# # Installed # #
from wait4it import wait_for, get_free_port

# # Project # #
import vigobusapi
from vigobusapi.vigobus_getters.mongo.client import get_collection
from vigobusapi.settings_handler import settings

__all__ = ("BaseTest",)


class BaseTest:
    api_port: int
    api_url: str
    api_process: Process

    @classmethod
    def setup_class(cls):
        cls.api_port = get_free_port()
        cls.api_url = f"http://localhost:{cls.api_port}"
        settings.api_port = cls.api_port

        cls.api_process = Process(target=vigobusapi.run)
        cls.api_process.start()
        wait_for(port=cls.api_port)

    @classmethod
    def teardown_class(cls):
        cls.api_process.terminate()

    @classmethod
    def teardown_method(cls):
        async def _clear_db():
            await collection.delete_many({})
        collection = get_collection(loop=asyncio.get_event_loop())
        asyncio.get_event_loop().run_until_complete(_clear_db())
