import asyncio

from aio_pika import IncomingMessage


from application.workers.transcriber import transcribe_youtube_video, transcribe_storage_file
from container import listener
from domain.enteties.IOdataenteties.queue_enteties import YoutubeTranscribationQuery,FileTranscribationQuery


@listener.consume('processor', 'transcribe_from_youtube_queue')
async def process_message(message: IncomingMessage):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()
    try:
        query = YoutubeTranscribationQuery.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic
    except ValueError as e:
        print(f"Error parsing message: {e}")
    asyncio.create_task(transcribe_youtube_video(youtube_url=query.url))


@listener.consume('processor', 'transcribe_from_storage_queue')
async def process_message(message: IncomingMessage):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()
    try:
        query = FileTranscribationQuery.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic
    except ValueError as e:
        print(f"Error parsing message: {e}")
    asyncio.create_task(transcribe_storage_file(file_url=query.url))

