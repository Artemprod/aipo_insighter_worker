#__run fast api application __

from src.database.repositories.repositories import Repositories
from src.database.repositories.sql_repo import DatabaseSessionManager
from src.api.app.initialize.server_creator import create_server
import uvicorn

url = "postgresql+asyncpg://postgres:1234@localhost:5432/text_process"
repositories = Repositories(DatabaseSessionManager(database_url=url))

server = create_server(repositories=repositories)

if __name__ == "__main__":
    uvicorn.run("server_app_run:server",  host="127.0.0.1", port=9192, lifespan="on")

