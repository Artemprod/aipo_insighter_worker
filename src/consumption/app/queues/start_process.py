import os
import tempfile
import asyncio
from datetime import datetime

from aio_pika import IncomingMessage

from container import listener
from src.api.routers.main_process.schemas import StartFromYouTubeMessage

from src.pipelines.base_pipeline import Pipeline, YoutubePipeline
from src.pipelines.models import PiplineData


@listener.consume('processor', 'transcribe_from_youtube_queue')
async def process_message(message: IncomingMessage, utils):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()

    try:
        query_message = StartFromYouTubeMessage.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic

        # Создание пайплайна
        pipeline_data = PiplineData(
            initiator_user_id=query_message.user_id,
            publisher_queue=query_message.publisher_queue,
            service_source=query_message.source,
            assistant_id=query_message.assistant_id,
            file_destination=query_message.youtube_url)
        print()
        pipeline = YoutubePipeline(repo=utils.database_repository,
                                   loader=utils.commands['loader']['youtube'],
                                   transcriber=utils.commands['transcriber']['assembly'],
                                   summarizer=utils.commands['summarizer']['chat_gpt'],
                                   publisher=utils.commands['publisher']['nats'], )

        # Запуск пайплайна
        await asyncio.create_task(pipeline.run(pipeline_data=pipeline_data))
    except ValueError as e:
        print(f"Error parsing message: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
