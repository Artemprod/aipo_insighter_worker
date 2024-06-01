import asyncio
import logging

from aiormq.abc import DeliveredMessage

from src.api.routers.main_process.schemas import StartFromYouTubeMessage
from src.pipelines.base_pipeline import YoutubePipeline
from src.pipelines.models import PiplineData


async def process_message(message: DeliveredMessage):
    print(f"Received message: {message.body.decode()}")
    try:
        query_message = StartFromYouTubeMessage.parse_raw(message.body.decode('utf-8'))
    except ValueError as e:
        print(f"Error parsing message: {e}")
        await message.channel.basic_nack(delivery_tag=message.delivery.delivery_tag, requeue=False)
        return None
    return query_message


async def create_pipeline(query_message, utils):
    pipeline_data = PiplineData(
        initiator_user_id=query_message.user_id,
        publisher_queue=query_message.publisher_queue,
        service_source=query_message.source,
        assistant_id=query_message.assistant_id,
        file_destination=query_message.youtube_url,
    )

    pipeline = YoutubePipeline(
        repo=utils.database_repository,
        loader=utils.commands['loader']['youtube'],
        transcriber=utils.commands['transcriber']['assembly'],
        summarizer=utils.commands['summarizer']['chat_gpt'],
        publisher=utils.commands['publisher']['nats'],
    )

    return pipeline, pipeline_data


async def run_pipeline(pipeline, pipeline_data, message):
    task = asyncio.create_task(pipeline.run(pipeline_data=pipeline_data))

    try:
        await task
        await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)
        print(f"Сообщение {message.delivery.routing_key} обработано")
    except Exception as e:
        print(f"Error in pipeline process: {e}")
        await message.channel.basic_nack(delivery_tag=message.delivery.delivery_tag, requeue=False)


async def on_message_from_youtube_queue(message: DeliveredMessage, utils):
    query_message = await process_message(message)
    if query_message:
        pipeline, pipeline_data = await create_pipeline(query_message, utils)
        await run_pipeline(pipeline, pipeline_data, message)
