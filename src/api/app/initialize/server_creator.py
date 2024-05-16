from typing import Optional
from fastapi import FastAPI
from src.api.app.initialize.lifspan import lifespan
from src.api.routers.assistant_routers import assistant_router
from src.api.routers.results_routers import results_router
from src.database.repositories.storage_container import Repositories

from src.api.routers.process_router import processes_router


def create_server(repositories: Optional[Repositories] = None):
    server = FastAPI(lifespan=lifespan, title="INSIGHTER APPLICATION")
    server.include_router(processes_router)
    server.include_router(assistant_router)
    server.include_router(results_router)
    server.repositories = repositories
    return server
