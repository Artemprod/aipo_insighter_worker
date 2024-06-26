import asyncio
import os
import tempfile
from datetime import datetime

from aio_pika import IncomingMessage

from container import listener
from src.api.routers.main_process.schemas import StartFromYouTubeMessage, StartFromS3
from src.pipelines.models import PiplineData


@listener.consume('processor', 'transcribe_from_youtube_queue')
async def process_message(message: IncomingMessage, utils):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()

    try:
        query_message = StartFromYouTubeMessage.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic

        # Создание временной директории
        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_file_path = os.path.normpath(
                os.path.join(str(tmpdirname), str(datetime.now().timestamp()), str(query_message.source),
                             str(query_message.user_id))
            )

            # Создание пайп лайна
            pipeline = utils.factory.create_youtube_pipeline(
                youtube_url=query_message.youtube_url,
                output_path=temp_file_path,
                pipeline_data=PiplineData(
                    initiator_user_id=query_message.user_id,
                    publisher_queue=query_message.publisher_queue,
                    service_source=query_message.source,
                    assistant_id=query_message.assistant_id
                )
            )

            # Запуск пайплайна
            await asyncio.create_task(pipeline.run())
    except ValueError as e:
        print(f"Error parsing message: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


@listener.consume('processor', 'transcribe_from_storage_queue')
async def storage_press_message(message: IncomingMessage, utils):
    json_str = message.body.decode()
    # TODO: Просто скачать файл с S3 сервера

    try:
        query_message: StartFromS3 = StartFromS3.parse_raw(
            json_str)  # Преобразование JSON строки в объект Pydantic

        # Создание временной директории
        # with tempfile.TemporaryDirectory() as tmpdirname:
        #     temp_file_path = os.path.normpath(
        #         os.path.join(str(tmpdirname), str(datetime.now().timestamp()), str(query_message.source),
        #                      str(query_message.user_id))
        #     )

            # Создание пайп лайна
            # pipeline = utils.factory.create_storage_pipeline(
            #     file_path=query_message.file_path,
            #     pipeline_data=PiplineData(
            #         initiator_user_id=query_message.user_id,
            #         publisher_queue=query_message.publisher_queue,
            #         service_source=query_message.source,
            #         assistant_id=query_message.assistant_id
            #     )
            # )

            # Запуск пайплайна
            # await asyncio.create_task(pipeline.run())
    except ValueError as e:
        print(f"Error parsing message: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
