from abc import ABC
from datetime import datetime

from faststream.nats import NatsBroker
from loguru import logger

from container import settings
from src.consumption.consumers.interface import ITranscriber, ISummarizer
from src.consumption.exeptions.summarize import NoResponseFromChatGptSummarization
from src.consumption.exeptions.trinscriber_exeptions import NoResponseFromAssembly, NoResponseWhisper
from src.consumption.models.publisher.triger import PublishTrigger, ErrorMessage
from src.database.repositories.storage_container import Repositories
from src.file_manager.exceptions.s3 import S3FileNotDownloaded
from src.file_manager.exceptions.youtube_loader import YoutubeAudioNotDownloaded
from src.file_manager.interface import IBaseFileLoader
from src.pipelines.models import PiplineData
from src.utils.path_opertaions import create_temp_path, clear_temp_dir, is_youtube_url, \
    create_s3_file_name, create_youtube_file_name
from src.utils.utils_exceptions import NoPath, NoYoutubeUrl


class Pipeline(ABC):
    temp_history_date = {}

    def __init__(self,
                 repo: Repositories,
                 loader: IBaseFileLoader,
                 transcriber: ITranscriber,
                 summarizer: ISummarizer,
                 ):

        self.repo = repo
        self.loader = loader
        self.transcriber = transcriber
        self.summarizer = summarizer

    async def run(self, pipeline_data: PiplineData) -> int | None:
        try:
            logger.info(f"Пайплайн запустился")
            temp_file_path = await self.create_temp_file_path(pipeline_data=pipeline_data)
            file = await self.loader(pipeline_data.file_destination, temp_file_path)
            transcribed_text = await self.transcriber(file)
            logger.info(f"получен транскриби рованый текст для пользвоателя {pipeline_data.initiator_user_id}")

            text_model = await self.save_transcribed_text(transcribed_text, pipeline_data)
            await self.publish_transcribed_text(text_model, pipeline_data)

            assistant = await self.repo.assistant_repository.get(assistant_id=pipeline_data.assistant_id)

            summary = await self.summarizer(transcribed_text=transcribed_text, assistant=assistant,
                                            user_prompt=pipeline_data.user_prompt)

            summary_text_model = await self.save_summary_text(summary=summary, pipeline_data=pipeline_data)
            await self.publish_summary_text(summary_text_model, pipeline_data)

            await self.save_new_history(transcribe_id=int(text_model.id),
                                        summary_id=int(summary_text_model.id),
                                        pipeline_data=pipeline_data)

        except NoPath as e:
            logger.exception("Произошла ошибка: отсутствует путь к файлу S3.")
            await self.publish_error(error=str(e), description="Не удалось извлечь путь до файла.",
                                     pipeline_data=pipeline_data)
            raise
        except NoYoutubeUrl as e:
            logger.exception("Произошла ошибка: отсутствует URL YouTube.")
            await self.publish_error(error=str(e), description="Не удалось извлечь URL YouTube.",
                                     pipeline_data=pipeline_data)
            raise
        except YoutubeAudioNotDownloaded as e:
            logger.exception("Произошла ошибка: не удалось скачать аудио с YouTube.")
            await self.publish_error(error=str(e), description="Не удалось скачать файл с YouTube.",
                                     pipeline_data=pipeline_data)
            raise
        except S3FileNotDownloaded as e:
            logger.exception("Произошла ошибка: не удалось скачать файл с S3.")
            await self.publish_error(error=str(e), description="Не удалось получить файл.",
                                     pipeline_data=pipeline_data)
            raise
        except NoResponseFromAssembly as e:
            logger.exception("Произошла ошибка: API Assembly не предоставил распознанный текст.")
            await self.publish_error(error=str(e),
                                     description="Не удалось получить распознанный текст.",
                                     pipeline_data=pipeline_data)
            raise
        except NoResponseWhisper as e:
            logger.exception("Произошла ошибка: API Whisper не предоставил распознанный текст.")
            await self.publish_error(error=str(e), description="Не удалось получить распознанный текст.",
                                     pipeline_data=pipeline_data)
            raise
        except NoResponseFromChatGptSummarization as e:
            logger.exception("Произошла ошибка: не удалось выполнить суммаризацию с помощью ChatGPT.")
            await self.publish_error(error=str(e), description="Не удалось выполнить суммаризацию",
                                     pipeline_data=pipeline_data)
            raise
        else:
            if temp_file_path:
                clear_temp_dir(temp_file_path)
                logger.info(f"Очистил временную папку {temp_file_path}")
            return 1

    async def save_transcribed_text(self, transcribed_text: str, pipeline_data: PiplineData):
        try:
            result = await self.repo.transcribed_text_repository.save(
                text=transcribed_text,
                user_id=pipeline_data.initiator_user_id,
                service_source=pipeline_data.service_source.value,
                transcription_date=datetime.now(),
                transcription_time=datetime.now()
            )
            logger.info(f"сохранил транскрибированый текст")
            return result
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в бд {e}")
            raise e

    async def save_summary_text(self, summary: str, pipeline_data: PiplineData):
        logger.info(f"сохраняю текст")
        return await self.repo.summary_text_repository.save(
            text=summary,
            user_id=pipeline_data.initiator_user_id,
            service_source=pipeline_data.service_source.value,
            summary_date=datetime.now()
        )

    async def save_new_history(self, transcribe_id: int, summary_id: int, pipeline_data: PiplineData):
        logger.info(f"сохраняю новую историю")
        return await self.repo.history_repository.add_history(
            user_id=int(pipeline_data.initiator_user_id),
            unique_id=str(pipeline_data.unique_id),
            service_source=str(pipeline_data.service_source.value),
            summary_id=summary_id,
            transcribe_id=transcribe_id)

    @staticmethod
    async def create_temp_file_path(pipeline_data: PiplineData):
        temp_file_path = None
        try:

            # если это не ютуб то cсоздаем имя файла из s3
            if not is_youtube_url(pipeline_data.file_destination):
                file_name = create_s3_file_name(path=pipeline_data.file_destination)
            else:
                file_name = create_youtube_file_name(youtube_url=pipeline_data.file_destination)
            if file_name is not None:
                temp_file_path = create_temp_path(file_name=file_name,
                                                  user_id=pipeline_data.initiator_user_id)
        except Exception:
            raise
        else:
            return temp_file_path

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

    @staticmethod
    async def publish_error(error, description, pipeline_data: PiplineData):
        async with NatsBroker(servers=settings.nats_publisher.nats_server_url) as broker:
            await broker.publish(
                message=ErrorMessage(error=error, description=description, user_id=pipeline_data.initiator_user_id),
                subject=f"{pipeline_data.publisher_queue}.error",

            )
            logger.info("Отправил саммари")
