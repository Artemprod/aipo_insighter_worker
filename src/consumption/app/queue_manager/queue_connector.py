import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel


class RabbitMQConnector:
    def __init__(self, username, password, rabbit_host='localhost'):
        self.channel = None
        self.connection = None
        self.username = username
        self.password = password
        self.rabbit_host = rabbit_host
        self.handlers = []

    async def connect(self):
        # Establish connection to RabbitMQ
        self.connection: AbstractRobustConnection = await aio_pika.connect_robust(
            f"amqp://{self.username}:{self.password}@{self.rabbit_host}"
        )
        self.channel: AbstractRobustChannel = await self.connection.channel()
        return self.connection
