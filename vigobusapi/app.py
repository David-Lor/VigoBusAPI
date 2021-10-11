"""APP
FastAPI initialization.
"""

# # Installed # #
import uvicorn
from fastapi import FastAPI

# # Project # #
from vigobusapi.routes import setup_routes
from vigobusapi.request_handler import request_handler
from vigobusapi.settings import settings
from vigobusapi.services import MongoDB
from vigobusapi.logger import logger

__all__ = ("app", "run")

app = FastAPI(
    title=settings.api_name
)
app.middleware("http")(request_handler)
setup_routes(app)


@app.on_event("startup")
async def app_setup():
    """This function runs when FastAPI starts, before accepting requests."""
    # Initialize MongoDB
    await MongoDB.initialize()


def run():
    """Run the API using Uvicorn
    """
    logger.info("Running the app with uvicorn")

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level
    )


if __name__ == '__main__':
    run()
