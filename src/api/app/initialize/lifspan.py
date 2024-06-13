from contextlib import asynccontextmanager
from typing import AsyncIterator
import aiormq
from aiormq.abc import AbstractConnection
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from container import settings, components
from retry import retry


async def rabit_mq_producer_connection():
    # инициализировать подключение к брокеру

    try:
        connection: AbstractConnection = await aiormq.connect(
            url=f"amqp://{settings.rabbitmq.rabitmq_user}:{settings.rabbitmq.rabitmq_password}@{settings.rabbitmq.rabitmq_host}:{settings.rabbitmq.rabitmq_port}")
        channel = await connection.channel()
        await channel.exchange_declare(exchange="exchanger", exchange_type="direct")
        print("Initialize rabit producer")
        return channel, connection
    except Exception as e:
        print("Failed connect to rabit", e)


@retry(TypeError, tries=5, delay=5)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Запущен инициализатор при сервере")
    FastAPICache.init(components.redis, prefix="fastapi-cache")
    channel, connection = await rabit_mq_producer_connection()
    app.state.rabit_mq_chanel = channel
    app.state.rabit_mq_connection = connection

    yield
    # закрыть подключение к брокеру
    await connection.close()
