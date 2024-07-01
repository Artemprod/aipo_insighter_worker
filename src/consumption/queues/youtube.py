import asyncio
import json

from aiormq.abc import DeliveredMessage
from loguru import logger

from src.api.routers.main_process.schemas import StartFromYouTubeMessage
from src.pipelines.base_pipeline import Pipeline
from src.pipelines.models import PiplineData


async def process_message(message):
    logger.info(f"Received message: {message}")
    query_message = StartFromYouTubeMessage(**message)
    return query_message


async def create_pipeline(query_message, utils):
    pipeline_data = PiplineData(
        unique_id=query_message.unique_id,
        initiator_user_id=query_message.user_id,
        publisher_queue=query_message.publisher_queue,
        service_source=query_message.source,
        assistant_id=query_message.assistant_id,
        file_destination=query_message.youtube_url,
    )

    pipeline: Pipeline = Pipeline(
        repo=utils.get("database_repository"),
        loader=utils.get("commands")['loader']['youtube'],
        transcriber=utils.get("commands")['transcriber']['assembly'],
        summarizer=utils.get("commands")['summarizer']['chat_gpt'],

    )

    return pipeline, pipeline_data


async def run_pipeline(pipeline, pipeline_data, message):
    await pipeline.run(pipeline_data=pipeline_data)
    logger.info(f"Сообщение {message} обработано")


async def on_message_from_youtube_queue(message, utils):
    query_message = await process_message(message)
    if query_message:
        pipeline, pipeline_data = await create_pipeline(query_message, utils)
        await run_pipeline(pipeline, pipeline_data, message)
