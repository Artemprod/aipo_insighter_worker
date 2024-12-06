from fastapi import APIRouter, Depends
from faststream.rabbit import RabbitBroker

from src.api.routers.main_process.rabbitmq import get_broker, publish_message
from src.api.routers.main_process.schemas import (
    StartFromS3Scheme,
    StartFromGoogleDriveScheme,
    get_responses,
)
from src.api.routers.main_process.schemas import StartFromYouTubeMessageScheme


processes_router = APIRouter(prefix="/start", tags=["Process"])


@processes_router.post(
    "/start_process_from_s3",
    responses=get_responses("S3")
)
async def start_task_from_storage(
        message: StartFromS3Scheme,
        broker: RabbitBroker = Depends(get_broker)
):
    await publish_message(broker, message, "storage_consumer")


@processes_router.post(
    "/start_process_from_youtube",
    responses=get_responses("YouTube")
)
async def start_task_from_youtube(
        message: StartFromYouTubeMessageScheme,
        broker: RabbitBroker = Depends(get_broker)
):
    await publish_message(broker, message, "youtube_consumer")


@processes_router.post(
    "/start_process_from_google_drive",
    responses=get_responses("Google Drive")
)
async def start_task_from_google_drive(
        message: StartFromGoogleDriveScheme,
        broker: RabbitBroker = Depends(get_broker)
):
    await publish_message(broker, message, "google_drive_consumer")
