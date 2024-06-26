import gc
import os
import shutil
import tempfile
from abc import ABC
from datetime import datetime
from pathlib import Path

from faststream.nats import NatsBroker
from loguru import logger

from container import settings
from src.consumption.consumers.interface import ITranscriber, ISummarizer
from src.database.repositories.interface import IRepositoryContainer
from src.file_manager.interface import IBaseFileLoader
from src.pipelines.models import PiplineData
from src.publishers.interface import IPublisher
from src.publishers.models import PublishTrigger
from src.utils.path_opertaions import parse_path, create_temp_path, clear_temp_dir


class Pipeline(ABC):

    def __init__(self,
                 repo: IRepositoryContainer,
                 loader: IBaseFileLoader,
                 transcriber: ITranscriber,
                 summarizer: ISummarizer,
                 publisher: IPublisher):

        self.repo = repo
        self.loader = loader
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.publisher = publisher



    async def run(self, pipeline_data: PiplineData) -> str | None:

        file_name = parse_path(path=pipeline_data.file_destination)
        temp_file_path = create_temp_path(file_name=file_name,
                                          user_id=pipeline_data.initiator_user_id)
        file = await self.loader(pipeline_data.file_destination, temp_file_path)
        transcribed_text = await self.transcriber(file)
        if not transcribed_text:
            logger.info("Нету транскрибированного текста")
            return None

        text_model = await self.save_transcribed_text(transcribed_text, pipeline_data)
        await self.publish_transcribed_text(text_model, pipeline_data)

        assistant = await self.repo.assistant_repository.get(assistant_id=pipeline_data.assistant_id)
        summary = await self.summarizer(transcribed_text=transcribed_text, assistant=assistant)

        if not summary:
            logger.info("Нету саммари")
            return None

        summary_text_model = await self.save_summary_text(summary, text_model.id, pipeline_data)
        await self.publish_summary_text(summary_text_model, pipeline_data)

        if temp_file_path:
            clear_temp_dir(temp_file_path)

        return summary

    async def save_transcribed_text(self, transcribed_text: str, pipeline_data: PiplineData):
        return await self.repo.transcribed_text_repository.save(
            text=transcribed_text,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source,
            transcription_date=datetime.now(),
            transcription_time=datetime.now()
        )

    @staticmethod
    async def publish_transcribed_text(text_model, pipeline_data: PiplineData):
        async with NatsBroker(servers=settings.nats_publisher.nats_server_url) as broker:
            await broker.publish(
                message=PublishTrigger(type="transcribation",
                                       tex_id=int(text_model.id),
                                       user_id=int(pipeline_data.initiator_user_id)),
                subject=f"{pipeline_data.publisher_queue}.transcribe",
            )

    async def save_summary_text(self, summary: str, transcribed_text_id: str, pipeline_data: PiplineData):
        return await self.repo.summary_text_repository.save(
            text=summary,
            transcribed_text_id=transcribed_text_id,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source,
            summary_date=datetime.now()
        )

    @staticmethod
    async def publish_summary_text(summary_text_model, pipeline_data: PiplineData):
        async with NatsBroker(servers=settings.nats_publisher.nats_server_url) as broker:
            await broker.publish(
                message=PublishTrigger(type="summary",
                                       tex_id=int(summary_text_model.id),
                                       user_id=int(pipeline_data.initiator_user_id)),
                subject=f"{pipeline_data.publisher_queue}.summary",


            )
