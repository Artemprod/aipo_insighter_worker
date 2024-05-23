import aio_pika
from aio_pika.abc import AbstractExchange, \
    DeliveryMode

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from src.api.routers.main_process.schemas import StartFromStorageMessage, StartFromYouTubeMessage, \
    StartFromStorageErrorResponse, StartFromYouTubeErrorResponse

processes_router = APIRouter(
    prefix='/start',
    tags=["Process"]
)


@processes_router.post("/start_process_from_storage")
async def start_task_from_storage(message: StartFromStorageMessage,
                                  request: Request):
    try:
        processor_exchange_object: AbstractExchange = request.app.state.process_exchange
        await processor_exchange_object.publish(
            aio_pika.Message(body=message.json().encode(),
                             delivery_mode=DeliveryMode.PERSISTENT),
            routing_key='transcribe_from_storage_queue', )
    except Exception as e:
        raise HTTPException(status_code=404,
                            detail=StartFromStorageErrorResponse(
                                user_id=message.user_id,
                                file_path=message.file_path,
                                storage_url=message.storage_url,
                                description=e,

                            ))


@processes_router.post("/start_process_from_youtube")
async def start_task_from_youtube(message: StartFromYouTubeMessage,
                                  request: Request):
    processor_exchange_object: AbstractExchange = request.app.state.process_exchange
    try:
        await processor_exchange_object.publish(
            aio_pika.Message(body=message.json().encode(),
                             delivery_mode=DeliveryMode.PERSISTENT),
            routing_key='transcribe_from_youtube_queue', )
    except Exception as e:
        raise HTTPException(status_code=404,
                            detail=StartFromYouTubeErrorResponse(
                                user_id=message.user_id,
                                youtube_url=message.youtube_url,
                                description=e,


                            ))

