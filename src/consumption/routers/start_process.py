import asyncio

from faststream.rabbit import RabbitRouter, RabbitQueue
from faststream import Context

from container import components
from src.consumption.queues.s3 import on_message_from_s3
from src.consumption.queues.youtube import on_message_from_youtube_queue

process_router = RabbitRouter(prefix="")


@process_router.subscriber(queue=RabbitQueue(name=components.rabit_consumers['youtube_consumer']['queue'],
                                             routing_key=components.rabit_consumers['youtube_consumer']['routing_key']),
                           exchange=components.rabit_consumers['youtube_consumer']['exchanger']['name'])
async def handle_youtube_response(msg, context=Context()):
    task = asyncio.create_task(on_message_from_youtube_queue(message=msg, utils=context.utils))
    task.add_done_callback(lambda t: t.exception() if t.exception() else None)


@process_router.subscriber(queue=RabbitQueue(name=components.rabit_consumers['storage_consumer']['queue'],
                                             routing_key=components.rabit_consumers['storage_consumer']['routing_key']),
                           exchange=components.rabit_consumers['storage_consumer']['exchanger']['name'])
async def handle_s3_response(msg, context=Context()):
    task = asyncio.create_task(on_message_from_s3(message=msg, utils=context.utils))
    task.add_done_callback(lambda t: t.exception() if t.exception() else None)
