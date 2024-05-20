# Абстрактный класс пайплайна
import gc
from datetime import datetime

from src.pipelines.models import PiplineData
from src.publishers.models import TranscribedTextTrigger, SummaryTextTrigger


class Pipeline:
    def __init__(self, repo, loader, file_cropper, transcriber,
                 summarizer, publisher, pipline_data: PiplineData):
        self.repo = repo
        self.loader = loader
        self.cropper = file_cropper
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.publisher = publisher
        self.pipline_data = pipline_data

    async def run(self):
        try:
            file = await self.loader()
            bunch_of_files = await self.cropper(file)
            transcribed_text = await self.transcriber(bunch_of_files)
            text_model = await self.repo.transcribed_text_repository.save(text=transcribed_text,
                                                                          initiator_user_id=self.pipline_data.initiator_user_id,
                                                                          transcription_date=datetime.now(),
                                                                          transcription_time=datetime.now())

            await self.publisher(result=TranscribedTextTrigger(tex_id=text_model.id,
                                                               user_id=self.pipline_data.initiator_user_id),
                                 queue=self.pipline_data.publisher_queue)
            summary = await self.summarizer(transcribed_text)
            summary_text_model = await self.repo.summary_text_repository.save(summary_text=summary,
                                                                              transcribed_text_id=text_model.id,
                                                                              user_id=self.pipline_data.initiator_user_id,
                                                                              summary_date=datetime.now())

            await self.publisher(result=SummaryTextTrigger(tex_id=summary_text_model.id,
                                                           user_id=self.pipline_data.initiator_user_id),
                                 queue=self.pipline_data.publisher_queue)
            return summary
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            self.cleanup()

    def cleanup(self):
        del self.loader
        del self.cropper
        del self.publisher
        del self.transcriber
        del self.summarizer
        gc.collect()
