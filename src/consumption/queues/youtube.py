from src.api.routers.main_process.schemas import StartFromYouTubeMessage
from src.pipelines.models import PiplineData
from src.consumption.queues.base_processor import BaseProcessor


class YouTubeProcessor(BaseProcessor):
    loader_key = 'youtube'

    @staticmethod
    def get_query_message(message):
        return StartFromYouTubeMessage(**message)

    @staticmethod
    def get_pipeline_data(query_message):
        return PiplineData(
            unique_id=query_message.unique_id,
            initiator_user_id=query_message.user_id,
            publisher_queue=query_message.publisher_queue,
            service_source=query_message.source,
            assistant_id=query_message.assistant_id,
            file_destination=query_message.youtube_url,
        )
