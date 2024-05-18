#__run fast api application __
from src.database.engine.session_maker import DatabaseSessionManager
from src.database.repositories.storage_container import Repositories

from src.api.app.initialize.server_creator import create_server
import uvicorn
from src.database.models.models_initializer import *

url = "postgresql+asyncpg://postgres:1234@localhost:5432/text_process"
repositories = Repositories(DatabaseSessionManager(database_url=url))


server = create_server(repositories=repositories)

if __name__ == "__main__":
    uvicorn.run("server_app_run:server",  host="127.0.0.1", port=9192, lifespan="on")

