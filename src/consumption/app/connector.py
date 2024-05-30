import asyncio
from typing import Callable

import aio_pika
from functools import wraps
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustQueue, AbstractExchange, \
    AbstractIncomingMessage, ExchangeType

from src.consumption.models.rabit.utils import Modules


class RabbitMQConnector:
    def __init__(self, username: str, password: str, port: int, rabbit_host: str = 'localhost'):
        self.connection: AbstractRobustConnection = None
        self.channel: AbstractRobustChannel = None
        self.username = username
        self.password = password
        self.port = port
        self.rabbit_host = rabbit_host
        self.utils = Modules

    async def connect(self) -> AbstractRobustConnection:
        self.connection = await aio_pika.connect_robust(
            f"amqp://{self.username}:{self.password}@{self.rabbit_host}:{self.port}"
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        return self.connection

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


class Consumer:
    def __init__(self, connector: RabbitMQConnector, exchange: str, queue: str, exchange_type: str, func: Callable):
        self.connector = connector
        self.exchange = exchange
        self.queue = queue
        self.exchange_type = exchange_type
        self.func = func

    async def start(self):
        print("Start consuming")
        exchange_object = await self.connector.channel.declare_exchange(
            name=self.exchange, type=ExchangeType(self.exchange_type)
        )
        queue_object = await self.connector.channel.declare_queue(name=self.queue, durable=True)
        await queue_object.bind(exchange_object)

        async def message_processor(message: AbstractIncomingMessage):
            async with message.process():
                try:
                    await self.func(message, self.connector.utils)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await message.nack(requeue=True)

        await queue_object.consume(message_processor)
