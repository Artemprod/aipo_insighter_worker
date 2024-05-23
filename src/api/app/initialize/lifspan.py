from contextlib import asynccontextmanager
from typing import AsyncIterator

from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from container import listener
from redis import asyncio as aioredis

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
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
