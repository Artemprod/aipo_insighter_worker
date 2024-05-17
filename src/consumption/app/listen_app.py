import asyncio

from aio_pika import IncomingMessage

from container import listener, whisper_client
from src.api.models.post_request_models.start_process import StartFromYouTubeMessage
from src.pipelines.pipline_factory import PipelineFactory

youtube_url = "https://www.youtube.com/watch?v=apKE_Htn_GQ"
file_path = r"D:\projects\AIPO_V2\insighter_worker\temp"
transcribe_model = whisper_client
llm = "gpt-4o"
max_response_tokens = 500
chunk_lents_seconds = 30
server_url="nats://demo.nats.io:4222"

@listener.consume('processor', 'transcribe_from_youtube_queue')
async def process_message(message: IncomingMessage):
    print(f"Received message: {message.body.decode()}")
    json_str = message.body.decode()
    try:
        query_message = StartFromYouTubeMessage.parse_raw(json_str)  # Преобразование JSON строки в объект Pydantic
        pipeline = PipelineFactory.create_youtube_pipeline(
            query_message.youtube_url, file_path, transcribe_model, llm, max_response_tokens, chunk_lents_seconds,
            transcribed_queue=StartFromYouTubeMessage.queue_transcribe,
            summary_queue=StartFromYouTubeMessage.queue_summary, server_url=server_url
        )
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
