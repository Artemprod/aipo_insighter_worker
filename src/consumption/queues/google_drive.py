from src.api.routers.main_process.schemas import StartFromGoogleDriveScheme
from src.consumption.models.consumption.queues import MessageType
from src.pipelines.models import PiplineData
from src.consumption.queues.base_processor import BaseProcessor


class GoogleDriveProcessor(BaseProcessor):
    loader_key = 'google_drive'

    @staticmethod
    def get_query_message(message: MessageType) -> StartFromGoogleDriveScheme:
        return StartFromGoogleDriveScheme(**message)

    @staticmethod
    def get_pipeline_data(query_message: StartFromGoogleDriveScheme) -> PiplineData:
        return PiplineData(
            unique_id=query_message.unique_id,
            initiator_user_id=query_message.user_id,
            publisher_queue=query_message.publisher_queue,
            service_source=query_message.source,
            assistant_id=query_message.assistant_id,
            file_destination=query_message.google_drive_url,
            user_prompt=query_message.user_prompt
        )
