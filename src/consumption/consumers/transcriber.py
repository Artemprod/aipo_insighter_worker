import asyncio
from typing import BinaryIO, Union

from assemblyai.api import ENDPOINT_UPLOAD, ENDPOINT_TRANSCRIPT
from src.consumption.consumers.interface import ITranscriber
from src.consumption.exeptions.trinscriber_exeptions import UnknownTranscriptionError, \
    APITranscriptionError, NoResponseFromAssembly, NoResponseWhisper

from src.file_manager.utils.interface import ICropper
from src.services.assembly.client import AssemblyClient, AsyncAssemblyClient
from src.services.openai_api_package.whisper_package.whisper import WhisperClient

import aiofiles
from aiogram.client.session import aiohttp

from assemblyai.types import TranscriptRequest, TranscriptResponse, TranscriptionConfig, TranscriptError

from tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt

from src.utils.data_utils import from_text, simple_from_text
from src.utils.wrappers import async_wrap


class WhisperTranscriber(ITranscriber):
    def __init__(self,
                 whisper_client: WhisperClient,
                 file_cropper: ICropper):
        self.cropper = file_cropper
        self.whisper_client = whisper_client

    async def transcribe(self, file_path: str) -> str:
        try:
            files = await self.cropper(file_path)
            tasks = [self.whisper_client.whisper_compile(file) for file in files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Соединяем результаты транскрипции в одну строку с учетом порядка файлов
            total_transcription = " ".join(result for result in results if isinstance(result, str))
        except Exception as e:
            raise NoResponseWhisper(f"Произошла ошибка: API Whisper не предоставил распознанный текст. \n"
                                    f"{str(e)}")
        else:
            return total_transcription

    async def __call__(self, file_path: str) -> str:
        return await self.transcribe(file_path)


class AssemblyTranscriber(ITranscriber):

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


class CostumeAssemblyTranscriber(ITranscriber):
    retry_request_timeout = 3.0  # Уменьшил время задержки между запросами

    def __init__(self, client: AsyncAssemblyClient, config: TranscriptionConfig = None):
        self.config = config or TranscriptionConfig(language_code="ru", dual_channel=True)
        self.client = client

    async def do_get_request(self, client: aiohttp.ClientSession, url: str, params=None):
        if params is None:
            params = {}
        async with client.get(url, params=params) as response:
            return response.status, await response.json()

    async def do_data_post_request(self, client: aiohttp.ClientSession, url: str, data):
        async with client.post(url, data=data) as response:
            return response.status, await response.json()

    async def do_json_post_request(self, client: aiohttp.ClientSession, url: str, json):
        async with client.post(url, json=json) as response:
            return response.status, await response.json()

    async def async_upload_file(self, client: aiohttp.ClientSession, file_path):
        async with aiofiles.open(file_path, "rb") as file:
            data = await file.read()
        status, response = await self.do_data_post_request(client=client, url=ENDPOINT_UPLOAD, data=data)
        if status != 200:
            raise TranscriptError(f"Failed to upload file: {response}")
        return response.get("upload_url")

    @retry(retry=retry_if_exception_type(TranscriptError), stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def async_create_transcript(self, client: aiohttp.ClientSession,
                                      request: TranscriptRequest) -> TranscriptResponse:
        status, response = await self.do_json_post_request(client=client, url=ENDPOINT_TRANSCRIPT,
                                                           json=request.dict(exclude_none=True, by_alias=True))
        if status != 200:
            raise TranscriptError(f"failed to transcribe url {request.audio_url}: {response.get('error')}")
        return TranscriptResponse.parse_obj(response)

    async def async_get_transcript(self, client: aiohttp.ClientSession, transcript_id) -> TranscriptResponse:
        url = f"{ENDPOINT_TRANSCRIPT}/{transcript_id}"
        status, response = await self.do_get_request(client=client, url=url)
        if status != 200:
            raise TranscriptError(f"Failed to get transcript status: {response.get('error')}")
        return TranscriptResponse.parse_obj(response)

    def create_transcript_obj(self, url) -> TranscriptRequest:
        return TranscriptRequest(audio_url=url, **self.config.raw.dict(exclude_none=True))

    @retry(retry=retry_if_exception_type((UnknownTranscriptionError, APITranscriptionError)),
           stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def async_wait_for_completion(self, client: aiohttp.ClientSession,
                                        transcript_response: TranscriptResponse) -> TranscriptResponse:
        while True:
            try:
                transcript = await self.async_get_transcript(client=client, transcript_id=transcript_response.id)
            except Exception as e:
                raise UnknownTranscriptionError(message=f"Non-API error occurred: {e}", transcriber=self.__class__)
            else:
                if transcript.status == transcript.status.error:
                    raise APITranscriptionError(message="Transcription error occurred", transcriber=self.__class__)
                elif transcript.status == transcript.status.completed:
                    return transcript
            await asyncio.sleep(self.retry_request_timeout)

    async def transcribe(self, file_path: Union[str, BinaryIO]) -> str:
        async with self.client.create_client() as client:
            file_url = await self.async_upload_file(client=client, file_path=file_path)
            transcript_request = self.create_transcript_obj(file_url)
            transcript = await self.async_create_transcript(client=client, request=transcript_request)
            response = await self.async_wait_for_completion(client=client, transcript_response=transcript)
            return from_text(response=response)

    async def __call__(self, file_path: Union[str, BinaryIO]) -> str:
        return await self.transcribe(file_path)


class AsyncWrappedAssemblyTranscriber(ITranscriber):

    def __init__(self, client: AssemblyClient, config: TranscriptionConfig = None):
        self.config = config or TranscriptionConfig(language_code="ru", speaker_labels=True, dual_channel=False)
        self.client = client

    @async_wrap
    def transcribe(self, file_path: Union[str, BinaryIO]):
        try:
            transcript = self.client.Transcriber().transcribe(file_path, self.config)
            result = simple_from_text(response=transcript, speaker_labels=self.config.speaker_labels)
        except Exception as e:
            raise NoResponseFromAssembly(f'Произошла ошибка: API Assembly не предоставил распознанный текст.\n'
                                         f' {str(e)}')
        else:
            return result

    async def __call__(self, file_path: Union[str, BinaryIO]) -> str:
        return await self.transcribe(file_path)
