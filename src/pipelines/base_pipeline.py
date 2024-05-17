# Абстрактный класс пайплайна
import gc
from datetime import datetime

from container import repositories_com
from src.database.repositories.transcribed_text_repository import TranscribedTextRepository


class Pipeline:
    def __init__(self, loader, file_cropper, transcriber,
                 summarizer, publisher, transcribed_queue, summary_queue):
        self.loader = loader
        self.cropper = file_cropper
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.publisher = publisher
        self.transcribed_queue = transcribed_queue
        self.summary_queue = summary_queue

    async def run(self):
        try:
            file = await self.loader()
            bunch_of_files = await self.cropper(file)
            transcribed_text = await self.transcriber(bunch_of_files)
            text_model = await repositories_com.transcribed_text_repository.save(text=transcribed_text,
                                                                                 initiator_user_id=123,
                                                                                 file_id=1,
                                                                                 transcription_date=datetime.now(),
                                                                                 transcription_time=datetime.now(),
                                                                                 model_id=1,
                                                                                 language_code="ru",
                                                                                 tags='123')

            self.publisher(text_model.id, self.transcribed_queue)
            summary = await self.summarizer(transcribed_text)
            summary_text_model = await repositories_com.summary_text_repository.save(text=summary,
                                                                                     transcribed_text_id=text_model.id,
                                                                                     user_id=123,
                                                                                     model_id=1,
                                                                                     summary_date=datetime.now(),
                                                                                     generation_time=datetime.now(),
                                                                                     tokens_requested=13,
                                                                                     tokens_generated=123)

            self.publisher(summary_text_model.id, self.summary_queue)
            return summary
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            self.cleanup()

    def cleanup(self):
        del self.loader
        del self.cropper
        del self.transcriber
        del self.summarizer
        gc.collect()
