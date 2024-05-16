import aio_pika

from aio_pika.abc import AbstractExchange, \
    DeliveryMode

from fastapi import APIRouter
from starlette.requests import Request

from src.api.models.post_request_models.start_process import StartFromYouTubeMessage, StartFromStorageMessage

processes_router = APIRouter()


@processes_router.post("/api/start/start_process_from_storage")
async def start_task_from_storage(message: StartFromStorageMessage,
                                  request: Request):
    processor_exchange_object: AbstractExchange = request.app.state.process_exchange
    await processor_exchange_object.publish(
        aio_pika.Message(body=message.json().encode(),
                         delivery_mode=DeliveryMode.PERSISTENT),
        routing_key='transcribe_from_storage_queue', )


@processes_router.post("/api/start/start_process_from_youtube")
async def start_task_from_youtube(message: StartFromYouTubeMessage,
                                  request: Request):
    processor_exchange_object: AbstractExchange = request.app.state.process_exchange
    await processor_exchange_object.publish(
        aio_pika.Message(body=message.json().encode(),
                         delivery_mode=DeliveryMode.PERSISTENT),
        routing_key='transcribe_from_youtube_queue', )
