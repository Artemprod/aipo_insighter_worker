import asyncio

from aio_pika import IncomingMessage

from application.workers.worker_piplines import youtube_pipline
from container import listener
from domain.enteties.IOdataenteties.queue_enteties import FileTranscribationQuery
from infrastructure.web.apps.fast_api_app.models.post_models import StartFromYouTubeMessage


@listener.consume('processor', 'transcribe_from_youtube_queue')
async def process_message(message: IncomingMessage):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()
    try:
        query_message = StartFromYouTubeMessage.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic
    except ValueError as e:
        print(f"Error parsing message: {e}")
    asyncio.create_task(youtube_pipline(youtube_url=query_message.youtube_url))


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