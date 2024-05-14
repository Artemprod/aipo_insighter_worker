from typing import Optional
from fastapi import FastAPI
from src.api.app.initialize.lifspan import lifespan
from src.database.repositories.repositories import Repositories
from src.api.routers.database_router import database_router
from src.api.routers.process_router import processes_router


def create_server(repositories: Optional[Repositories] = None):
    server = FastAPI(lifespan=lifespan, title="INSIGHTER APPLICATION")
    server.include_router(processes_router)
    server.include_router(database_router)
    server.repositories = repositories
    return server
