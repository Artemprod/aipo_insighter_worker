import gc
import os
import tempfile
from abc import ABC
from datetime import datetime

from src.consumption.consumers.interface import ITranscriber, ISummarizer
from src.database.repositories.interface import IRepositoryContainer
from src.file_manager.interface import IBaseFileLoader
from src.pipelines.models import PiplineData
from src.publishers.interface import IPublisher
from src.publishers.models import TranscribedTextTrigger, SummaryTextTrigger


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
        try:
            transcribed_text = await self._run(pipeline_data)
            # Сохранение транскрибированного текста
            text_model = await self.repo.transcribed_text_repository.save(
                text=transcribed_text,
                user_id=pipeline_data.initiator_user_id,
                service_source=pipeline_data.service_source,
                transcription_date=datetime.now(),
                transcription_time=datetime.now()
            )

            # Публикация результата транскрибированного текста
            await self.publisher(
                result=TranscribedTextTrigger(tex_id=text_model.id, user_id=pipeline_data.initiator_user_id),
                queue=pipeline_data.publisher_queue
            )

            # Получение помощника для суммаризации
            assistant = await self.repo.assistant_repository.get(assistant_id=pipeline_data.assistant_id)
            # Суммаризация текста

            summary = await self.summarizer(transcribed_text=transcribed_text,
                                            assistant=assistant)

            # Сохранение суммарного текста
            summary_text_model = await self.repo.summary_text_repository.save(
                text=summary,
                transcribed_text_id=text_model.id,
                user_id=pipeline_data.initiator_user_id,
                service_source=pipeline_data.service_source,
                summary_date=datetime.now()
            )

            # Публикация результата суммарного текста
            await self.publisher(
                result=SummaryTextTrigger(tex_id=summary_text_model.id, user_id=pipeline_data.initiator_user_id),
                queue=pipeline_data.publisher_queue
            )

            return summary
        except Exception as e:
            # Улучшенное логирование ошибок
            print(f"An error occurred: {e}")
            return None
        finally:
            # Очистка ресурсов
            await self.cleanup()

    async def cleanup(self):
        self.loader = None
        self.publisher = None
        self.transcriber = None
        self.summarizer = None
        gc.collect()


class YoutubePipeline(Pipeline):

    async def _run(self, pipeline_data: PiplineData):
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            temp_file_path = os.path.normpath(
                os.path.join(str(tmp_dir_name), str(datetime.now().timestamp()),
                             str(pipeline_data.service_source),
                             str(pipeline_data.initiator_user_id))
            )
            file = await self.loader(pipeline_data.file_destination, temp_file_path)
            transcribed_text = await self.transcriber(file)
            return transcribed_text
