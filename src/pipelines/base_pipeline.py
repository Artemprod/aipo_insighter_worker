import gc
from datetime import datetime

from src.pipelines.models import PiplineData
from src.publishers.models import TranscribedTextTrigger, SummaryTextTrigger


class Pipeline:
    def __init__(self, repo, loader, file_cropper, transcriber, summarizer, publisher, pipeline_data: PiplineData):
        self.repo = repo
        self.loader = loader
        self.cropper = file_cropper
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.publisher = publisher
        self.pipeline_data = pipeline_data

    async def run(self):
        try:
            file = await self.loader()
            bunch_of_files = await self.cropper(file)
            transcribed_text = await self.transcriber(bunch_of_files)

            # Сохранение транскрибированного текста
            text_model = await self.repo.transcribed_text_repository.save(
                text=transcribed_text,
                user_id=self.pipeline_data.initiator_user_id,
                service_source=self.pipeline_data.service_source,
                transcription_date=datetime.now(),
                transcription_time=datetime.now()
            )

            # Публикация результата транскрибированного текста
            await self.publisher(
                result=TranscribedTextTrigger(tex_id=text_model.id, user_id=self.pipeline_data.initiator_user_id),
                queue=self.pipeline_data.publisher_queue
            )

            # Получение помощника для суммаризации
            assistant = await self.repo.assistant_repository.get(assistant_id=self.pipeline_data.assistant_id)

            # Суммаризация текста
            summary = await self.summarizer(transcribed_text, assistant)

            # Сохранение суммарного текста
            summary_text_model = await self.repo.summary_text_repository.save(
                text=summary,
                transcribed_text_id=text_model.id,
                user_id=self.pipeline_data.initiator_user_id,
                service_source=self.pipeline_data.service_source,
                summary_date=datetime.now()
            )

            # Публикация результата суммарного текста
            await self.publisher(
                result=SummaryTextTrigger(tex_id=summary_text_model.id, user_id=self.pipeline_data.initiator_user_id),
                queue=self.pipeline_data.publisher_queue
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
