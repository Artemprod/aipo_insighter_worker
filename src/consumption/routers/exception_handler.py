from asyncio import Task
from faststream.nats import NatsBroker
from loguru import logger

from container import settings
from src.consumption.models.publisher.triger import ErrorMessage
from src.pipelines.models import PiplineData


async def error_callback(task: Task, message: dict):
    try:
        result = task.result()
    except Exception as e:
        error_message = str(e)
        description = "Ошибка при обработке сообщения"
        logger.error(f"{description}: {error_message} \n"
                     f"Пступившее сообщение: {message}")
        await publish_error(error=error_message, description=description, message=message)


async def publish_error(error: str, description: str, message: dict):
    async with NatsBroker(servers=settings.nats_publisher.nats_server_url) as broker:
        await broker.publish(
            message=ErrorMessage(error=error, description=description, user_id=message.get("user_id")),
            subject=f"{message.get('publisher_queue')}.error",
        )
        logger.info("Отправил сообщение об ошибке")
