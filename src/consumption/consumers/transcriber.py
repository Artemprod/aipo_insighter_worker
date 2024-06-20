import asyncio
from typing import List, BinaryIO, Union

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.consumption.consumers.interface import ITranscriber
from src.file_manager.utils.interface import ICropper
from src.services.assembly.client import AssemblyClient
from src.services.openai_api_package.whisper_package.whisper import WhisperClient
from src.utils.wrappers import async_wrap


class WhisperTranscriber(ITranscriber):
    def __init__(self,
                 whisper_client: WhisperClient,
                 file_cropper: ICropper):
        self.cropper = file_cropper
        self.whisper_client = whisper_client

    async def transcribe(self, file_path: str) -> str:
        files = await self.cropper(file_path)
        tasks = [self.whisper_client.whisper_compile(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Соединяем результаты транскрипции в одну строку с учетом порядка файлов
        total_transcription = " ".join(result for result in results if isinstance(result, str))
        return total_transcription

    async def __call__(self, file_path: str) -> str:
        return await self.transcribe(file_path)


class AssemblyTranscriber:

    def __init__(self, assembly_client: AssemblyClient,
                 language_code='ru',
                 speaker_labels=True):
        self.assembly_client = assembly_client
        self.language_code = language_code
        self.speaker_labels = speaker_labels

    async def transcribe(self, file_path: Union[str, BinaryIO]) -> str:
        config = self.assembly_client.TranscriptionConfig(
            speaker_labels=self.speaker_labels,
            language_code=self.language_code
        )
        transcriber = self.assembly_client.Transcriber()
        future_transcript = transcriber.transcribe_async(file_path, config=config)
        transcript = future_transcript.result()
        text = ""
        for utterance in transcript.utterances:
            text += f"Speaker {utterance.speaker}: {utterance.text}\n\n"
        return text

    async def __call__(self, file_path: Union[str, BinaryIO]) -> str:
        return await self.transcribe(file_path)
