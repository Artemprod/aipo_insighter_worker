from src.api.routers.main_process.schemas import StartFromS3Scheme
from src.pipelines.models import PiplineData
from src.consumption.queues.base_processor import BaseProcessor


class S3Processor(BaseProcessor):
    loader_key = 's3'

    def get_query_message(self, message):
        return StartFromS3Scheme(**message)

    def get_pipeline_data(self, query_message):
        return PiplineData(
            unique_id=query_message.unique_id,
            initiator_user_id=query_message.user_id,
            publisher_queue=query_message.publisher_queue,
            service_source=query_message.source,
            assistant_id=query_message.assistant_id,
            file_destination=query_message.s3_path,
        )
