from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from faststream.rabbit import RabbitBroker
from loguru import logger

from container import settings, components


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Запущен инициализатор при сервере")
    FastAPICache.init(components.redis, prefix="fastapi-cache")
    broker = RabbitBroker(f"amqp://{settings.rabbitmq.rabitmq_user}:"
                          f"{settings.rabbitmq.rabitmq_password}@"
                          f"{settings.rabbitmq.rabitmq_host}:{settings.rabbitmq.rabitmq_port}")
    await broker.connect()
    app.state.broker = broker
    print()
    yield
    # закрыть подключение к брокеру
