# __run fast api application __
import sentry_sdk

from container import components, settings
from src.api.app.initialize.server_creator import create_server
import uvicorn

server = create_server(repositories=components.repositories_com)

if __name__ == "__main__":
    uvicorn.run("server_app_run:server",
                host=settings.uvicorn_server.uvicorn_host,
                port=9192,
                lifespan="on",
                log_level="debug",
                reload=False)
