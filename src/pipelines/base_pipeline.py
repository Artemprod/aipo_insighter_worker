import asyncio
import gc
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from container import repositories_com
from src.database.repositories.storage_container import Repositories
from src.pipelines.models import PiplineData
from src.publishers.models import TranscribedTextTrigger, SummaryTextTrigger


class Pipeline:
    #TODO вынести в отдельный класс
    repo:Repositories = repositories_com
    loader:Any
    file_cropper:Any
    transcriber:Any
    summarizer:Any
    publisher:Any


 ##TODO есть run которые запускает все есть часть для всех классов а есть изменяем
    @abstractmethod
    async def _run(self,pipeline_data: PiplineData):
      pass
      ##TODO Здесь логика не изменяемая постоянная для всех
    async def run(self, pipeline_data: PiplineData) ->str | None:
        try:
            await self._run()
            # file = await self.loader()
            # bunch_of_files = await self.cropper(file)
            transcribed_text = await self.transcriber(bunch_of_files)

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
            summary = await self.summarizer(transcribed_text, assistant)

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
        self.cropper = None
        self.publisher = None
        self.transcriber = None
        self.summarizer = None
        gc.collect()

class YoutubePipline(Pipeline):

    async def _run(self,pipeline_data: PiplineData):
        # тут изменяемая логика
        return None

class Storageipline(Pipeline):
    async def _run(self, pipeline_data: PiplineData):
        pass