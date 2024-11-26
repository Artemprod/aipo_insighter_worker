import pytest

from assemblyai.types import TranscriptionConfig

from src.consumption.consumers.transcriber import AsyncWrappedAssemblyTranscriber
from src.consumption.exeptions.trinscriber_exeptions import APITranscriptionError
from src.services.assembly.client import AssemblyClient


@pytest.fixture
def async_assembly_transcriber():
    config = TranscriptionConfig(language_code="ru", speaker_labels=True, dual_channel=False)
    return AsyncWrappedAssemblyTranscriber(
        client=AssemblyClient(api_key='api_key'),
        config=config
    )


@pytest.mark.asyncio
class TestAsyncWrappedAssemblyTranscriber:
    async def test_transcribe_success(self, async_assembly_transcriber, mocker):
        mock_transcript = {"text": "mocked transcription"}
        mock_result = "formatted transcription result"

        mocker.patch.object(
            async_assembly_transcriber.client.Transcriber,
            'transcribe',
            return_value=mock_transcript
        )

        mock_simple_from_text = mocker.patch(
            "src.consumption.consumers.transcriber.from_text",
            return_value=mock_result
        )

        file_path = "test_audio.mp3"
        result = await async_assembly_transcriber.transcribe(file_path)

        assert result == mock_result
        async_assembly_transcriber.client.Transcriber().transcribe.assert_called_once_with(
            file_path,
            async_assembly_transcriber.config
        )
        mock_simple_from_text.assert_called_once_with(response=mock_transcript)

    async def test_transcribe_failure(self, async_assembly_transcriber, mocker):
        mocker.patch.object(
            async_assembly_transcriber.client.Transcriber,
            'transcribe',
            side_effect=APITranscriptionError("Mocked Exception")
        )

        file_path = "test_audio.mp3"

        with pytest.raises(APITranscriptionError) as exc_info:
            await async_assembly_transcriber.transcribe(file_path)

        assert "Mocked Exception" in str(exc_info.value)
        async_assembly_transcriber.client.Transcriber().transcribe.assert_called_once_with(
            file_path,
            async_assembly_transcriber.config
        )

    async def test_call_success(self, async_assembly_transcriber, mocker):
        mock_transcript = {"text": "mocked transcription"}
        mock_result = "formatted transcription result"
        mocker.patch.object(
            async_assembly_transcriber.client.Transcriber,
            'transcribe',
            return_value=mock_transcript
        )

        mock_simple_from_text = mocker.patch(
            "src.consumption.consumers.transcriber.from_text",
            return_value=mock_result
        )

        file_path = "test_audio.mp3"
        result = await async_assembly_transcriber(file_path)

        assert result == mock_result
        async_assembly_transcriber.client.Transcriber().transcribe.assert_called_once_with(
            file_path, async_assembly_transcriber.config
        )
        mock_simple_from_text.assert_called_once_with(response=mock_transcript)
