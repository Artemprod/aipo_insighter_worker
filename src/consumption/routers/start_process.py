import asyncio

from faststream.rabbit import RabbitRouter, RabbitQueue, RabbitMessage
from faststream import Context

from container import components
from src.consumption.queues.s3 import on_message_from_s3
from src.consumption.queues.youtube import on_message_from_youtube_queue

process_router = RabbitRouter(prefix="")


async def handle_task_result(task, msg):
    try:
        exception = task.exception()
        if exception:
            await msg.nack(
                requeue=True)  # Сообщаем, что сообщение не было обработано и нужно повторно добавить в очередь
        else:
            await msg.ack()  # Подтверждаем успешную обработку сообщения
    except Exception as e:
        await msg.nack(requeue=True)


@process_router.subscriber(queue=RabbitQueue(name=components.rabit_consumers['youtube_consumer']['queue'],
                                             routing_key=components.rabit_consumers['youtube_consumer']['routing_key']),
                           exchange=components.rabit_consumers['youtube_consumer']['exchanger']['name'])
async def handle_youtube_response(msg: RabbitMessage, context=Context()):
    task = asyncio.create_task(on_message_from_youtube_queue(message=msg, utils=context.utils))
    task.add_done_callback(lambda t: asyncio.create_task(handle_task_result(t, msg)))


@process_router.subscriber(queue=RabbitQueue(name=components.rabit_consumers['storage_consumer']['queue'],
                                             routing_key=components.rabit_consumers['storage_consumer']['routing_key']),
                           exchange=components.rabit_consumers['storage_consumer']['exchanger']['name'])
async def handle_s3_response(msg: RabbitMessage, context=Context()):
    task = asyncio.create_task(on_message_from_s3(message=msg, utils=context.utils))
    task.add_done_callback(lambda t: asyncio.create_task(handle_task_result(t, msg)))
