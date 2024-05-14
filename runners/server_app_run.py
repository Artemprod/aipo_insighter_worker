#__run fast api application __

from infrastructure.database.database_repository.repositories import Repositories
from infrastructure.database.database_repository.sql_repo import DatabaseSessionManager
from runners.runer_fuctions.server_app_runer import create_server
import uvicorn

url = "postgresql+asyncpg://postgres:1234@localhost:5432/text_process"
repositories = Repositories(DatabaseSessionManager(database_url=url))

server = create_server(repositories=repositories)

if __name__ == "__main__":
    uvicorn.run("server_app_run:server",  host="127.0.0.1", port=9192, lifespan="on")

