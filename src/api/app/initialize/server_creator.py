from typing import Optional

from fastapi import FastAPI

from src.api.app.initialize.lifspan import lifespan
from src.api.routers.assistant.router import assistant_router
from src.api.routers.main_process.router import processes_router
from src.api.routers.results.router import results_router
from src.database.repositories.storage_container import Repositories


def create_server(repositories: Optional[Repositories] = None):
    server = FastAPI(lifespan=lifespan,
                     title="INSIGHTER APPLICATION",
                     )
    server.include_router(processes_router)
    server.include_router(assistant_router)
    server.include_router(results_router)
    server.repositories = repositories
    return server
