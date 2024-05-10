from contextlib import asynccontextmanager
from typing import Optional

from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from fastapi import FastAPI

from container import listener
from infrastructure.database.database_repository.repositories import Repositories

from infrastructure.web.apps.fast_api_app.endpoints.database_endpoints import database_router
from infrastructure.web.apps.fast_api_app.endpoints.process_endpoints import processes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # инициализировать подключение к брокеру
    connection: AbstractRobustConnection = await listener.connect()
    channel: AbstractRobustChannel = await connection.channel()
    process_exchange = await channel.declare_exchange(name='processor', type='direct')
    await channel.declare_queue(name='transcribe_from_youtube_queue', durable=True)
    await channel.declare_queue(name='transcribe_from_storage_queue', durable=True)
    app.state.chanel = channel
    app.state.process_exchange = process_exchange
    yield
    # закрыть подключение к брокеру
    await connection.close()


def create_server(repositories: Optional[Repositories] = None):
    server = FastAPI(lifespan=lifespan, title="INSIGHTER APPLICATION")
    server.include_router(processes_router)
    server.include_router(database_router)
    server.repositories = repositories
    return server
