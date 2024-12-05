import pytest

from src.consumption.consumers.transcriber import WhisperTranscriber


class MockWhisperClient:
    async def whisper_compile(self, file):
        if file == "file1.mp4":
            return "Transcription 1"
        elif file == "file2.mp4":
            return "Transcription 2"
        elif file == "file_exception_1.mp4":
            raise ValueError
        elif file == "file_exception_2.mp4":
            raise ValueError
        raise Exception("Some error")


class MockFileCropper:
    async def __call__(self, file_path):
        if file_path == "path/to/file.mp4":
            return ["file1.mp4", "file2.mp4"]
        elif file_path == "path/to/file_with_exception":
            return ["file_exception_1.mp4", "file_exception_2.mp4"]
        raise Exception("Some error")


@pytest.fixture
def whisper_transcriber():
    whisper_client = MockWhisperClient()
    cropper = MockFileCropper()
    return WhisperTranscriber(whisper_client=whisper_client, file_cropper=cropper)


@pytest.mark.asyncio
async def test_whisper_transcribe_success(whisper_transcriber):
    result = await whisper_transcriber("path/to/file.mp4")

    assert result == "Transcription 1 Transcription 2"


@pytest.mark.asyncio
async def test_transcribe_file_whisper_compile_exception(whisper_transcriber):
    async def raise_exception(file):
        raise ValueError()

    whisper_transcriber.whisper_client.whisper_compile = raise_exception

    res = await whisper_transcriber("path/to/file.mp4")
    assert res == ""


@pytest.mark.asyncio
async def test_whisper_transcribe_with_mixed_responses(whisper_transcriber):
    async def mixed_responses(file):
        if file == "file1.mp4":
            return "Transcription 1"
        elif file == "file2.mp4":
            return None
        raise Exception("Some error")

    whisper_transcriber.whisper_client.whisper_compile = mixed_responses

    result = await whisper_transcriber.transcribe("path/to/file.mp4")
    assert result == "Transcription 1"
