from typing import BinaryIO, Union

from src.consumption.consumers.interface import ITranscriber
from src.consumption.exeptions.trinscriber_exeptions import NoResponseFromAssembly

from src.services.assembly.client import AssemblyClient

from assemblyai.types import TranscriptionConfig


from src.utils.data_utils import simple_from_text
from src.utils.wrappers import async_wrap


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
