import asyncio
from typing import Callable
from src.consumption.app.connector import RabbitMQConnector


class Consumer:
    def __init__(self,
                 connector: RabbitMQConnector,
                 queue: str,
                 routing_key: str,
                 exchange: str,
                 exchange_type: str,
                 func: Callable,
                 prefetch_count: int = 1,
                 no_ack: bool = False
                 ) -> None:

        self.connector = connector
        self.queue = queue
        self.routing_key = routing_key
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.func = func
        self.prefetch_count = prefetch_count
        self.no_ack = no_ack

    async def start(self) -> None:
        await self.initialize_consumer()
        await asyncio.Future()

    async def initialize_consumer(self) -> None:
        connection = await self.connector.connect()
        channel = await connection.channel()

        await channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)
        declare_ok = await channel.queue_declare(self.queue)

        await channel.queue_bind(
            queue=declare_ok.queue,
            exchange=self.exchange,
            routing_key=self.routing_key
        )

        await channel.basic_qos(prefetch_count=self.prefetch_count)

        await channel.basic_consume(
            queue=declare_ok.queue,
            consumer_callback=self.func,
            no_ack=self.no_ack
        )