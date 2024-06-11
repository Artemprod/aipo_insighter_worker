import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


import aiormq

from aiormq.abc import AbstractConnection
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


from container import settings, components


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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(components.redis, prefix="fastapi-cache")
    channel, connection = await rabit_mq_producer_connection()
    app.state.rabit_mq_chanel = channel
    app.state.rabit_mq_connection = connection

    yield
    # закрыть подключение к брокеру
    await connection.close()
