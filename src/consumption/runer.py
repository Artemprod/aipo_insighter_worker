import asyncio
import os
import sys
from functools import partial
from container import components, listener
from src.consumption.app.consumer import Consumer
from src.consumption.app.queues.s3 import on_message_from_s3
from src.consumption.app.queues.youtube import on_message_from_youtube_queue




async def main():
    consumers = []

    for consumer, configs in components.rabit_consumers.items():
        if consumer == "youtube_consumer":
            consumer_instance = Consumer(
                connector=listener,
                queue=configs['queue'],
                routing_key=configs['routing_key'],
                exchange=configs['exchanger']['name'],
                exchange_type=configs['exchanger']['type'],
                func=partial(on_message_from_youtube_queue, utils=listener.utils),
                prefetch_count=1,
                no_ack=False
            )
            consumers.append(consumer_instance)
        elif consumer == "storage_consumer":
            consumer_instance = Consumer(
                connector=listener,
                queue=configs['queue'],
                routing_key=configs['routing_key'],
                exchange=configs['exchanger']['name'],
                exchange_type=configs['exchanger']['type'],
                func=partial(on_message_from_s3, utils=listener.utils),
                prefetch_count=1,
                no_ack=False
            )
            consumers.append(consumer_instance)
    await asyncio.gather(*[consumer.start() for consumer in consumers])


if __name__ == "__main__":
    asyncio.run(main())
