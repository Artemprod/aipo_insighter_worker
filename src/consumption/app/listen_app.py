import asyncio
import tempfile

from aio_pika import IncomingMessage

from container import listener
from src.api.routers.main_process.schemas import StartFromYouTubeMessage
from src.pipelines.models import PiplineData



youtube_url = "https://www.youtube.com/watch?v=apKE_Htn_GQ"


@listener.consume('processor', 'transcribe_from_youtube_queue')
async def process_message(message: IncomingMessage, utils):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()
    try:
        query_message = StartFromYouTubeMessage.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic
        with tempfile.TemporaryDirectory() as tmpdirname:
            pipeline = utils.factory.create_youtube_pipeline(youtube_url=query_message.youtube_url,
                                                             output_path=f"{tmpdirname}{query_message.user_id}",
                                                             pipline_data=PiplineData(
                                                                 initiator_user_id=query_message.user_id,
                                                                 publisher_queue=query_message.publisher_queue,
                                                             ))
            asyncio.create_task(pipeline.run())
    except ValueError as e:
        print(f"Error parsing message: {e}")


# @listener.consume('processor', 'transcribe_from_storage_queue')
# async def process_message(message: IncomingMessage):
#     print(f"Received message: {message.body.decode()}")
#     json_str = message.body.decode()
#     try:
#         query = FileTranscribationQuery.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic
#     except ValueError as e:
#         print(f"Error parsing message: {e}")
#     asyncio.create_task(pipline(file_url=query.url))

if __name__ == "__main__":
    asyncio.run(listener.start_consume())
