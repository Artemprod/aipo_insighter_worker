import aio_pika
from aio_pika.abc import AbstractExchange, DeliveryMode

from src.api.routers.main_process.schemas import StartFromYouTubeMessage, \
    StartFromS3

from aiormq.abc import AbstractChannel, AbstractConnection
from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from container import components, settings
from src.api.routers.main_process.schemas import StartFromStorageMessage, StartFromYouTubeMessage, \
    StartFromStorageErrorResponse, StartFromYouTubeErrorResponse

processes_router = APIRouter(
    prefix='/start',
    tags=["Process"]
)


@processes_router.post("/start_process_from_s3")
async def start_task_from_storage(message: StartFromS3, request: Request):
    chanel: AbstractChannel = request.app.state.rabit_mq_chanel
    try:
        print(chanel)
        await chanel.basic_publish(
            body=message.json().encode('utf-8'),
            exchange=components.rabit_consumers['storage_consumer']['exchanger']['name'],
            routing_key=components.rabit_consumers['storage_consumer']['routing_key']
        )

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=StartFromStorageErrorResponse(
                user_id=message.user_id,
                file_path=message.file_path,
                storage_url=message.storage_url,
                description=e,
            )
        )


@processes_router.post("/start_process_from_youtube")
async def start_task_from_youtube(message: StartFromYouTubeMessage,
                                  request: Request):
    chanel: AbstractChannel = request.app.state.rabit_mq_chanel
    try:
        print(chanel)
        await chanel.basic_publish(
            body=message.json().encode('utf-8'),
            exchange=components.rabit_consumers['youtube_consumer']['exchanger']['name'],
            routing_key=components.rabit_consumers['youtube_consumer']['routing_key']
        )

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=StartFromYouTubeErrorResponse(
                user_id=message.user_id,
                youtube_url=message.youtube_url,
                description=e,

            )
        )
