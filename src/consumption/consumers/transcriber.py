import asyncio
from typing import List

from src.services.openai_api_package.whisper_package.whisper import WhisperClient


class BaseTranscriber:
    def __init__(self, transcribe_model):
        self.transcribe_model = transcribe_model


class WhisperTranscriber(BaseTranscriber):
    def __init__(self, transcribe_model: WhisperClient):
        super().__init__(transcribe_model)

    async def transcribe_bunch(self, files: List[str]) -> str:
        # Запускаем все задачи параллельно и собираем их результаты в порядке передачи
        tasks = [self.transcribe_model.whisper_compile(file_path=file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Соединяем результаты транскрипции в одну строку с учетом порядка файлов
        total_transcription = " ".join(result for result in results if isinstance(result, str))
        return total_transcription

    async def __call__(self, files: List[str]) -> str:
        return await self.transcribe_bunch(files)

#
# async def download_file(url, path: str):
#     return r"C:\Users\artem\OneDrive\Рабочий стол\Тестовые данные\WEBM mini.webm"
#
#
# @publisher.publish(queue="transcribe")
# async def transcribe_storage_file(file_url: str):
#     # TODO Поставить временный файлы
#     file = await download_file(url=file_url,
#                                path=r"/temp")  # использует агента скачивания
#     print('file downloaded')
#     record_id: int = await transcribe(file)
#
#     # преообразовать в данные для отправки
#     return TranscribedTextId(
#         id_text=record_id,
#         addressee=None,
#         description=None,
#     ).json()
