import asyncio

from src.file_manager.media_file_cropper import crop_file
from src.services.openai_api_package.whisper_package.whisper import WhisperClient
from src.services.youtube_package.youtube import download_video_from_youtube


class BaseTranscriber:

    def __init__(self, transcribe_model):
        self.transcribe_model = transcribe_model


class WisperTranscriber(BaseTranscriber):

    def __init__(self, transcribe_model: WhisperClient):
        super().__init__(transcribe_model)
        self.transcribe_model = transcribe_model

    async def transcribe_bunch(self, files: list):
        tasks = []
        for file in files:
            tasks.append(asyncio.create_task(self.transcribe_model.whisper_compile(file_path=file)))
        result = await asyncio.gather(*tasks)
        total_transcription = " ".join(result)
        return total_transcription





async def download_file(url, path: str):
    return r"C:\Users\artem\OneDrive\Рабочий стол\Тестовые данные\WEBM mini.webm"





@publisher.publish(queue="transcribe")
async def transcribe_storage_file(file_url: str):
    # TODO Поставить временный файлы
    file = await download_file(url=file_url,
                               path=r"/temp")  # использует агента скачивания
    print('file downloaded')
    record_id: int = await transcribe(file)

    # преообразовать в данные для отправки
    return TranscribedTextId(
        id_text=record_id,
        addressee=None,
        description=None,
    ).json()
