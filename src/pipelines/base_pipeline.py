from abc import ABC
from datetime import datetime
from faststream.nats import NatsBroker
from loguru import logger

from container import settings
from src.file_manager.types import FilePath
from src.consumption.consumers.interface import ITranscriber, ISummarizer
from src.consumption.models.publisher.triger import ErrorMessage
from src.consumption.models.consumption.asssistant import AIAssistant
from src.consumption.models.publisher.triger import PublishTrigger
from src.database.repositories.storage_container import Repositories
from src.file_manager.base_file_manager import BaseFileManager
from src.pipelines.models import PiplineData


class Pipeline(ABC):
    temp_history_date = {}

    def __init__(self,
                 repo: Repositories,
                 loader: BaseFileManager,
                 transcriber: ITranscriber,
                 summarizer: ISummarizer,
                 ):

        self.repo = repo
        self.loader = loader
        self.transcriber = transcriber
        self.summarizer = summarizer

    async def run(self, pipeline_data: PiplineData) -> int | None:
        logger.info("Пайплайн запустился")
        temp_file_path = None

        try:
            temp_file_path: FilePath = await self.loader.start_load(pipeline_data)
            transcribed_text, transcribed_text_id = await self.transcribe_file(temp_file_path, pipeline_data)
            assistant = await self.repo.assistant_repository.get(assistant_id=pipeline_data.assistant_id)
            summary_id = await self.make_summary(transcribed_text, assistant, pipeline_data)

            await self.save_new_history(
                transcribe_id=transcribed_text_id,
                summary_id=summary_id,
                pipeline_data=pipeline_data
            )
            return 1

        except Exception:
            raise

        finally:
            self.loader.clear_temp_directory(temp_file_path)

    async def transcribe_file(self, file_path: str, pipeline_data: PiplineData) -> tuple[str, int]:
        transcribed_text: str = await self.transcriber(file_path)
        logger.info(f"получен транскриби рованый текст для пользвоателя {pipeline_data.initiator_user_id}")
        text_model = await self.save_transcribed_text(transcribed_text, pipeline_data)
        await self.publish_transcribed_text(text_model, pipeline_data)
        return transcribed_text, int(text_model.id)

    async def make_summary(self, transcribed_text: str, assistant: AIAssistant, pipeline_data: PiplineData) -> int:
        summary = await self.summarizer(transcribed_text=transcribed_text, assistant=assistant)
        summary_text_model = await self.save_summary_text(summary=summary, pipeline_data=pipeline_data)
        await self.publish_summary_text(summary_text_model, pipeline_data)
        return int(summary_text_model.id)

    async def save_transcribed_text(self, transcribed_text: str, pipeline_data: PiplineData):
        result = await self.repo.transcribed_text_repository.save(
            text=transcribed_text,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source,
            transcription_date=datetime.now(),
            transcription_time=datetime.now()
        )
        logger.info("сохранил транскрибированый текст")
        return result

    async def save_new_history(self, transcribe_id: int, summary_id: int, pipeline_data: PiplineData):
        logger.info("сохраняю новую историю")
        return await self.repo.history_repository.add_history(
            user_id=int(pipeline_data.initiator_user_id),
            unique_id=str(pipeline_data.unique_id),
            service_source=str(pipeline_data.service_source),
            summary_id=summary_id,
            transcribe_id=transcribe_id)

    async def save_summary_text(self, summary: str, pipeline_data: PiplineData):
        logger.info("сохраняю текст")
        return await self.repo.summary_text_repository.save(
            text=summary,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source,
            summary_date=datetime.now()
        )

    @staticmethod
    async def publish_transcribed_text(text_model, pipeline_data: PiplineData):
        async with NatsBroker(servers=settings.nats_publisher.nats_server_url) as broker:
            await broker.publish(
                message=PublishTrigger(type="transcribation",
                                       unique_id=pipeline_data.unique_id,
                                       tex_id=int(text_model.id),
                                       user_id=int(pipeline_data.initiator_user_id)),
                subject=f"{pipeline_data.publisher_queue}.transcribe",
            )
            logger.info("Отправил транскрибацию")

    @staticmethod
    async def publish_summary_text(summary_text_model, pipeline_data: PiplineData):
        async with NatsBroker(servers=settings.nats_publisher.nats_server_url) as broker:
            await broker.publish(
                message=PublishTrigger(type="summary",
                                       unique_id=pipeline_data.unique_id,
                                       tex_id=int(summary_text_model.id),
                                       user_id=int(pipeline_data.initiator_user_id)),
                subject=f"{pipeline_data.publisher_queue}.summary",

            )
            logger.info("Отправил саммари")
