import asyncio
import json
from loguru import logger
from faststream.rabbit import RabbitRouter, RabbitQueue, RabbitMessage
from faststream import Context

from container import components
from src.consumption.queues.s3 import on_message_from_s3
from src.consumption.queues.youtube import on_message_from_youtube_queue

process_router = RabbitRouter(prefix="")


async def handle_task_result(task, msg: RabbitMessage):
    try:
        exception = task.exception()
        if exception:
            logger.error(f"Ошибка обработки асинхронной задачи: {exception}")
            await msg.nack(requeue=True)  # Сообщаем, что сообщение не было обработано и нужно повторно добавить в очередь
            raise Exception(exception)
        else:
            logger.info(f"Сообщение обработано успешно: {msg}")
            await msg.ack()  # Подтверждаем успешную обработку сообщения
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await msg.nack(requeue=True)
        raise e


@process_router.subscriber(queue=RabbitQueue(name=components.rabit_consumers['youtube_consumer']['queue'],
                                             routing_key=components.rabit_consumers['youtube_consumer']['routing_key']),
                           exchange=components.rabit_consumers['youtube_consumer']['exchanger']['name'])
async def handle_youtube_response(msg: RabbitMessage, context=Context()):
    task = asyncio.create_task(on_message_from_youtube_queue(message= json.loads(msg.body.decode("utf-8")), utils=context.utils))
    task.add_done_callback(lambda t:handle_task_result(t, msg))


@process_router.subscriber(queue=RabbitQueue(name=components.rabit_consumers['storage_consumer']['queue'],
                                             routing_key=components.rabit_consumers['storage_consumer']['routing_key']),
                           exchange=components.rabit_consumers['storage_consumer']['exchanger']['name'])
async def handle_s3_response(msg: RabbitMessage, context=Context()):
    task = asyncio.create_task(on_message_from_s3(message=json.loads(msg.body.decode("utf-8")), utils=context.utils))
    task.add_done_callback(lambda t: handle_task_result(t, msg))
