import asyncio
import aio_pika
from functools import wraps
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustQueue, AbstractExchange

class Utils:
    def func(self):
        raise NotImplementedError
class RabbitMQConnector:
    def __init__(self, username, password, port, rabbit_host='localhost'):
        self.username = username
        self.password = password
        self.port = port
        self.rabbit_host = rabbit_host
        self.handlers = []
        self.utils = Utils

    async def connect(self):
        # Establish connection to RabbitMQ
        self.connection: AbstractRobustConnection = await aio_pika.connect_robust(
            f"amqp://{self.username}:{self.password}@{self.rabbit_host}:{self.port}"
        )
        self.channel: AbstractRobustChannel = await self.connection.channel()
        return self.connection

    def consume(self, exchange, queue, exchange_type='direct'):
        def decorator(func):
            self.handlers.append((exchange, queue, exchange_type, func))

            @wraps(func)
            async def wrapper(*args, **kwargs):
                await func(*args, **kwargs)

            return wrapper

        return decorator

    async def start_consume(self):
        print('Start consuming ...')
        await self.connect()
        for exchange, queue, exchange_type, func in self.handlers:
            exchange_object: AbstractExchange = await self.channel.declare_exchange(name=exchange, type=exchange_type)
            queue_object: AbstractRobustQueue = await self.channel.declare_queue(name=queue, durable=True)
            await queue_object.bind(exchange_object)

            async def message_processor(message: IncomingMessage, func=func):
                async with message.process():
                    await func(message,self.utils)

            await queue_object.consume(message_processor)

        try:
            await asyncio.Future()  # Run forever
        finally:
            await self.connection.close()

    def set_utils(self, utils):
        self.utils = utils
