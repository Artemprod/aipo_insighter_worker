import gc
import os
import shutil
import tempfile
from abc import ABC
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.consumption.consumers.interface import ITranscriber, ISummarizer
from src.database.repositories.interface import IRepositoryContainer
from src.file_manager.interface import IBaseFileLoader
from src.pipelines.models import PiplineData
from src.publishers.interface import IPublisher
from src.publishers.models import TranscribedTextTrigger, SummaryTextTrigger, PublishTrigger
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

    async def _run(self, pipeline_data: PiplineData):
        raise NotImplementedError

    async def run(self, pipeline_data: PiplineData) -> str | None:
        temp_file_path = None
        try:
            temp_file_path = await self._run(pipeline_data)
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

            return summary

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            return None
        finally:
            if temp_file_path:
                clear_temp_dir(temp_file_path)
            await self.cleanup()

    async def save_transcribed_text(self, transcribed_text: str, pipeline_data: PiplineData):
        return await self.repo.transcribed_text_repository.save(
            text=transcribed_text,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source,
            transcription_date=datetime.now(),
            transcription_time=datetime.now()
        )

    async def publish_transcribed_text(self, text_model, pipeline_data: PiplineData):
        await self.publisher(
            result=PublishTrigger(type="transcribation", tex_id=text_model.id, user_id=pipeline_data.initiator_user_id),
            queue=pipeline_data.publisher_queue
        )

    async def save_summary_text(self, summary: str, transcribed_text_id: str, pipeline_data: PiplineData):
        return await self.repo.summary_text_repository.save(
            text=summary,
            transcribed_text_id=transcribed_text_id,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source,
            summary_date=datetime.now()
        )

    async def publish_summary_text(self, summary_text_model, pipeline_data: PiplineData):
        await self.publisher(
            result=PublishTrigger(type='summary', tex_id=summary_text_model.id,
                                  user_id=pipeline_data.initiator_user_id),
            queue=pipeline_data.publisher_queue
        )

    async def cleanup(self):
        self.loader = None
        self.publisher = None
        self.transcriber = None
        self.summarizer = None
        gc.collect()


class YoutubePipeline(Pipeline):

    async def _run(self, pipeline_data: PiplineData):
        logger.info("запуск YoutubePipeline")
        try:
            temp_file_path = create_temp_path(file_name=None,
                                              user_id=pipeline_data.initiator_user_id)
            return temp_file_path
        except Exception as e:
            logger.exception(f"Ошибка создания временной директории {e}")


class S3ipipeline(Pipeline):

    async def _run(self, pipeline_data: PiplineData) -> str:
        logger.info("запуск S3ipipeline")
        try:

            file_name = parse_path(path=pipeline_data.file_destination)
            temp_file_path = create_temp_path(file_name=file_name,
                                              user_id=pipeline_data.initiator_user_id)

            return temp_file_path
        except Exception as e:
            logger.exception(f"Ошибка создания временной директории {e}")
