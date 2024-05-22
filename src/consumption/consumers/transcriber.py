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

