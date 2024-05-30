from contextlib import asynccontextmanager
from typing import AsyncIterator

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from container import settings



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # инициализировать подключение к брокеру
    connection: AbstractRobustConnection = await aio_pika.connect_robust(
            f"amqp://{settings.rabbitmq.rabitmq_user}:{settings.rabbitmq.rabitmq_password}@{settings.rabbitmq.rabitmq_host}:{settings.rabbitmq.rabitmq_port}")

    channel: AbstractRobustChannel = await connection.channel()
    process_exchange = await channel.declare_exchange(name='processor', type='direct')
    await channel.declare_queue(name='transcribe_from_youtube_queue', durable=True)
    await channel.declare_queue(name='transcribe_from_storage_queue', durable=True)
    app.state.chanel = channel
    app.state.process_exchange = process_exchange

    yield
    # закрыть подключение к брокеру
    await connection.close()
