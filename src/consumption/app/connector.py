import aiormq
from aiormq.abc import AbstractConnection
from src.consumption.models.rabit.utils import Modules


class RabbitMQConnector:
    def __init__(self, username: str, password: str, port: int, rabbit_host: str = 'localhost'):
        self.channel = None
        self.connection: AbstractConnection = None
        self.username = username
        self.password = password
        self.port = port
        self.rabbit_host = rabbit_host
        self.utils = Modules

    async def connect(self) -> AbstractConnection:
        self.connection: AbstractConnection = await aiormq.connect(
            url=f"amqp://{self.username}:{self.password}@{self.rabbit_host}:{self.port}")
        return self.connection

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
