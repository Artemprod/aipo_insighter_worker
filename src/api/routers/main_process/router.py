from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from container import components
from src.api.routers.main_process import schemas

processes_router = APIRouter(
    prefix='/start',
    tags=["Process"]
)


@processes_router.post("/start_process_from_s3", response_model=schemas.StartFromS3Response)
async def start_task_from_storage(message: schemas.StartFromS3, request: Request):
    """Начать процесс из локального хранилища"""
    broker: RabbitBroker = request.app.state.broker
    await broker.publish(
        message=message.json().encode('utf-8'),
        queue=RabbitQueue(name=components.rabit_consumers['storage_consumer']['queue'],
                          routing_key=components.rabit_consumers['storage_consumer']['routing_key']),
        exchange=RabbitExchange(components.rabit_consumers['storage_consumer']['exchanger']['name']))
    return JSONResponse({"status": "queued"}, status_code=status.HTTP_201_CREATED)


@processes_router.post("/start_process_from_youtube", response_model=schemas.StartFromYouTubeMessageResponse)
async def start_task_from_youtube(message: schemas.StartFromYouTubeMessage, request: Request):
    """Начать процесс из YouTube"""
    broker: RabbitBroker = request.app.state.broker
    await broker.publish(
        message=message.json().encode('utf-8'),
        queue=RabbitQueue(name=components.rabit_consumers['youtube_consumer']['queue'],
                          routing_key=components.rabit_consumers['youtube_consumer']['routing_key']),
        exchange=RabbitExchange(components.rabit_consumers['youtube_consumer']['exchanger']['name']))
    return JSONResponse({"status": "queued"}, status_code=status.HTTP_201_CREATED)
