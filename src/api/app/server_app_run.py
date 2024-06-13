# __run fast api application __
from container import components
from src.api.app.initialize.server_creator import create_server
import uvicorn

server = create_server(repositories=components.repositories_com)

if __name__ == "__main__":
    uvicorn.run("server_app_run:server", host="0.0.0.0", port=9192, lifespan="on")
