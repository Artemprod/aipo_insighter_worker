
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from src.api.routers.main_process.schemas import StartFromYouTubeMessage, \
    StartFromS3

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from container import components
from src.api.routers.main_process.schemas import StartFromYouTubeMessage, \
    StartFromStorageErrorResponse, StartFromYouTubeErrorResponse

processes_router = APIRouter(
    prefix='/start',
    tags=["Process"]
)


@processes_router.post("/start_process_from_s3")
async def start_task_from_storage(message: StartFromS3, request: Request):
    broker: RabbitBroker = request.app.state.broker
    await broker.publish(
        message=message.json().encode('utf-8'),
        queue=RabbitQueue(name=components.rabit_consumers['storage_consumer']['queue'],
                          routing_key=components.rabit_consumers['storage_consumer']['routing_key']),
        exchange=RabbitExchange(components.rabit_consumers['storage_consumer']['exchanger']['name']))


@processes_router.post("/start_process_from_youtube")
async def start_task_from_youtube(message: StartFromYouTubeMessage,
                                  request: Request):
    broker: RabbitBroker = request.app.state.broker
    await broker.publish(
        message=message.json().encode('utf-8'),
        queue=RabbitQueue(name=components.rabit_consumers['youtube_consumer']['queue'],
                          routing_key=components.rabit_consumers['youtube_consumer']['routing_key']),
        exchange=RabbitExchange(components.rabit_consumers['youtube_consumer']['exchanger']['name']))
