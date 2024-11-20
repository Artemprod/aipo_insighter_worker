from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientError
from assemblyai import TranscriptError
from assemblyai.api import ENDPOINT_TRANSCRIPT
from assemblyai.types import TranscriptRequest, TranscriptResponse, TranscriptionConfig
from pytest_mock import mocker
from tenacity import RetryError

from src.consumption.consumers.transcriber import WhisperTranscriber, AssemblyTranscriber, CostumeAssemblyTranscriber, \
    AsyncWrappedAssemblyTranscriber
from src.consumption.exeptions.trinscriber_exeptions import UnknownTranscriptionError, \
    APITranscriptionError
from src.services.assembly.client import AsyncAssemblyClient, AssemblyClient


# ===================WhisperTranscriber====================
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


# ===================AssemblyTranscriber====================

class MockAssemblyClient:
    class TranscriptionConfig:
        def __init__(self, speaker_labels, language_code):
            self.speaker_labels = speaker_labels
            self.language_code = language_code

    class Transcriber:
        def transcribe_async(self, file_path, config):
            return MockTranscribeAsync(file_path, config)


class MockTranscribeAsync:
    def __init__(self, file_path, config):
        self.file_path = file_path
        self.config = config

    def result(self):
        return MockTranscript(speaker_labels=self.config.speaker_labels)


class MockTranscript:
    def __init__(self, speaker_labels):
        self.speaker_labels = speaker_labels

    @property
    def utterances(self):
        if self.speaker_labels:
            return [
                MockUtterance(speaker="1", text="Hello, how are you?"),
                MockUtterance(speaker="2", text="I'm fine, thank you!"),
            ]
        else:
            return [
                MockUtterance(speaker=None, text="Hello, how are you?"),
                MockUtterance(speaker=None, text="I'm fine, thank you!"),
            ]


class MockUtterance:
    def __init__(self, speaker, text):
        self.speaker = speaker
        self.text = text


@pytest.fixture
def assembly_transcriber():
    assembly_client = MockAssemblyClient()
    return AssemblyTranscriber(assembly_client=assembly_client)


@pytest.mark.asyncio
async def test_transcribe_success(assembly_transcriber):
    result = await assembly_transcriber.transcribe("path/to/file.mp4")
    expected_result = "Speaker 1: Hello, how are you?\n\nSpeaker 2: I'm fine, thank you!\n\n"
    assert result == expected_result


@pytest.mark.asyncio
async def test_transcribe_with_different_language(assembly_transcriber):
    assembly_transcriber.language_code = 'en'
    result = await assembly_transcriber.transcribe("path/to/file.mp4")
    expected_result = "Speaker 1: Hello, how are you?\n\nSpeaker 2: I'm fine, thank you!\n\n"
    assert result == expected_result


@pytest.mark.asyncio
async def test_transcriber_without_speaker_labels():
    assembly_client = MockAssemblyClient()
    transcriber = AssemblyTranscriber(assembly_client, speaker_labels=False)
    result = await transcriber.transcribe("mock_file_path")
    expected_result = "Speaker None: Hello, how are you?\n\nSpeaker None: I'm fine, thank you!\n\n"
    assert result == expected_result


# ===================CostumeAssemblyTranscriber====================

class MockResponse:
    def __init__(self, status, json_data):
        self.status = status
        self._json_data = json_data

    async def json(self):
        return self._json_data

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


url = "http://example.com/api"
params = {"key": "value"}
mock_success_response = MockResponse(200, {"data": "some data"})
mock_fail_response = MockResponse(404, {})


@pytest.fixture
def costume_assembly_transcriber():
    client = AsyncAssemblyClient(api_key='api_key')
    return CostumeAssemblyTranscriber(client=client)


@pytest.fixture
async def get_costume_assembly_transcriber_client(costume_assembly_transcriber):
    async with costume_assembly_transcriber.client.create_client() as client:
        return client


@pytest.mark.asyncio
async def test_do_get_request_success(costume_assembly_transcriber, get_costume_assembly_transcriber_client, mocker):
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_success_response)

    status, response = await costume_assembly_transcriber.do_get_request(
        await get_costume_assembly_transcriber_client,
        url,
        params
    )

    assert status == 200
    assert response == {"data": "some data"}


@pytest.mark.asyncio
async def test_do_get_request_success_without_params(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_success_response)

    status, response = await costume_assembly_transcriber.do_get_request(
        await get_costume_assembly_transcriber_client,
        url,
        {}
    )

    assert status == 200
    assert response == {"data": "some data"}


@pytest.mark.asyncio
async def test_do_get_request_failure(costume_assembly_transcriber, get_costume_assembly_transcriber_client, mocker):
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_fail_response)

    status, response = await costume_assembly_transcriber.do_get_request(
        await get_costume_assembly_transcriber_client,
        url,
        params
    )

    assert status == 404
    assert response == {}


@pytest.mark.asyncio
async def test_do_get_request_exception(costume_assembly_transcriber, get_costume_assembly_transcriber_client, mocker):
    mocker.patch('aiohttp.ClientSession.get', side_effect=ClientError("Network error"))

    with pytest.raises(ClientError):
        await costume_assembly_transcriber.do_get_request(
            await get_costume_assembly_transcriber_client,
            url,
            params
        )


@pytest.mark.asyncio
async def test_do_data_post_request_success(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', return_value=mock_success_response)

    status, response = await costume_assembly_transcriber.do_data_post_request(
        await get_costume_assembly_transcriber_client,
        url,
        params
    )

    assert status == 200
    assert response == {"data": "some data"}


@pytest.mark.asyncio
async def test_do_data_post_request_success_without_data(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', return_value=mock_success_response)

    status, response = await costume_assembly_transcriber.do_data_post_request(
        await get_costume_assembly_transcriber_client,
        url,
        {}
    )

    assert status == 200
    assert response == {"data": "some data"}


@pytest.mark.asyncio
async def test_do_data_post_request_failure(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', return_value=mock_fail_response)

    status, response = await costume_assembly_transcriber.do_data_post_request(
        await get_costume_assembly_transcriber_client,
        url,
        params
    )

    assert status == 404
    assert response == {}


@pytest.mark.asyncio
async def test_do_data_post_request_exception(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', side_effect=ClientError("Network error"))

    with pytest.raises(ClientError):
        await costume_assembly_transcriber.do_data_post_request(
            await get_costume_assembly_transcriber_client,
            url,
            params
        )


@pytest.mark.asyncio
async def test_do_json_post_request_success(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', return_value=mock_success_response)

    status, response = await costume_assembly_transcriber.do_json_post_request(
        await get_costume_assembly_transcriber_client,
        url,
        params
    )

    assert status == 200
    assert response == {"data": "some data"}


@pytest.mark.asyncio
async def test_do_json_post_request_success_without_data(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', return_value=mock_success_response)

    status, response = await costume_assembly_transcriber.do_json_post_request(
        await get_costume_assembly_transcriber_client,
        url,
        {}
    )

    assert status == 200
    assert response == {"data": "some data"}


@pytest.mark.asyncio
async def test_do_json_post_request_failure(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', return_value=mock_fail_response)

    status, response = await costume_assembly_transcriber.do_json_post_request(
        await get_costume_assembly_transcriber_client,
        url,
        params
    )

    assert status == 404
    assert response == {}


@pytest.mark.asyncio
async def test_do_json_post_request_exception(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', side_effect=ClientError("Network error"))

    with pytest.raises(ClientError):
        await costume_assembly_transcriber.do_json_post_request(
            await get_costume_assembly_transcriber_client,
            url,
            params
        )


@pytest.mark.asyncio
async def test_do_json_post_request_without_url(
        costume_assembly_transcriber,
        get_costume_assembly_transcriber_client,
        mocker
):
    mocker.patch('aiohttp.ClientSession.post', side_effect=ClientError("Network error"))

    with pytest.raises(ClientError):
        await costume_assembly_transcriber.do_json_post_request(
            await get_costume_assembly_transcriber_client,
            url,
            params
        )


@pytest.mark.asyncio
async def test_async_upload_file_success(costume_assembly_transcriber, mocker):
    mock_file = AsyncMock()
    mock_file.__aenter__.return_value.read.return_value = b"file content"

    mocker.patch("aiofiles.open", return_value=mock_file)

    mocker.patch.object(
        costume_assembly_transcriber,
        'do_data_post_request',
        return_value=(200, {"upload_url": "http://example.com/upload"})
    )

    upload_url = await costume_assembly_transcriber.async_upload_file(
        costume_assembly_transcriber.client,
        "path/to/file"
    )

    assert upload_url == "http://example.com/upload"
    costume_assembly_transcriber.do_data_post_request.assert_called_once()


@pytest.mark.asyncio
async def test_async_upload_file_failure(costume_assembly_transcriber, mocker):
    mock_file = AsyncMock()
    mock_file.__aenter__.return_value.read.return_value = b"file content"

    mocker.patch("aiofiles.open", return_value=mock_file)

    mocker.patch.object(
        costume_assembly_transcriber,
        'do_data_post_request',
        return_value=(400, {"error": "Bad Request"})
    )

    with pytest.raises(TranscriptError, match="Failed to upload file: {'error': 'Bad Request'}"):
        await costume_assembly_transcriber.async_upload_file(
            costume_assembly_transcriber.client,
            "path/to/file"
        )


@pytest.mark.asyncio
async def test_async_upload_file_file_open_error(costume_assembly_transcriber, mocker):
    mocker.patch("aiofiles.open", side_effect=FileNotFoundError("File not found"))

    with pytest.raises(FileNotFoundError, match="File not found"):
        await costume_assembly_transcriber.async_upload_file(
            costume_assembly_transcriber.client,
            "path/to/nonexistent_file"
        )


@pytest.mark.asyncio
async def test_async_create_transcript_success(costume_assembly_transcriber, mocker):
    request_data = TranscriptRequest(audio_url="http://example.com/audio.mp3")
    mock_response = {
        "audio_url": "http://example.com/audio.mp3",
        "status": "completed",
    }
    mocker.patch.object(
        costume_assembly_transcriber,
        'do_json_post_request',
        return_value=(200, mock_response)
    )

    response = await costume_assembly_transcriber.async_create_transcript(
        costume_assembly_transcriber.client,
        request_data
    )

    assert response.audio_url == "http://example.com/audio.mp3"
    assert response.status == "completed"


@pytest.mark.asyncio
async def test_async_create_transcript_failure(costume_assembly_transcriber, mocker):
    request_data = TranscriptRequest(audio_url="http://example.com/audio.mp3")
    mock_response = {
        "audio_url": "http://example.com/audio.mp3",
        "status": "failed",
        "error": "Transcription failed."
    }

    mock_post = mocker.patch.object(
        costume_assembly_transcriber,
        'do_json_post_request',
        return_value=(400, mock_response)
    )

    with pytest.raises(RetryError) as exc_info:
        await costume_assembly_transcriber.async_create_transcript(costume_assembly_transcriber.client, request_data)

    assert isinstance(exc_info.value.last_attempt.exception(), TranscriptError)
    assert mock_post.call_count == 3


@pytest.mark.asyncio
async def test_async_get_transcript_success(costume_assembly_transcriber, mocker):
    transcript_id = "12345"
    mock_response = {
        "audio_url": "http://example.com/audio.mp3",
        "status": "completed",
        "text": "This is the transcription text."
    }

    mocker.patch.object(
        costume_assembly_transcriber,
        'do_get_request',
        return_value=(200, mock_response)
    )

    response = await costume_assembly_transcriber.async_get_transcript(
        costume_assembly_transcriber.client,
        transcript_id
    )

    assert response.audio_url == "http://example.com/audio.mp3"
    assert response.status == "completed"
    assert response.text == "This is the transcription text."


@pytest.mark.asyncio
async def test_async_get_transcript_failure(costume_assembly_transcriber, mocker):
    transcript_id = "12345"
    mock_response = {
        "error": "Transcript not found"
    }

    mocker.patch.object(
        costume_assembly_transcriber,
        'do_get_request',
        return_value=(404, mock_response)
    )

    with pytest.raises(TranscriptError) as exc_info:
        await costume_assembly_transcriber.async_get_transcript(costume_assembly_transcriber.client, transcript_id)

    assert "Failed to get transcript status" in str(exc_info.value)
    assert "Transcript not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_get_transcript_missing_error_field(costume_assembly_transcriber, mocker):
    transcript_id = "12345"
    mock_response = {}

    mocker.patch.object(
        costume_assembly_transcriber,
        'do_get_request',
        return_value=(500, mock_response)
    )

    with pytest.raises(TranscriptError) as exc_info:
        await costume_assembly_transcriber.async_get_transcript(costume_assembly_transcriber.client, transcript_id)

    assert "Failed to get transcript status" in str(exc_info.value)
    assert "None" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_get_transcript_do_get_request_called_correctly(costume_assembly_transcriber, mocker):
    transcript_id = "12345"
    mock_response = {
        "audio_url": "http://example.com/audio.mp3",
        "status": "completed",
        "text": "This is the transcription text."
    }

    mock_do_get = mocker.patch.object(
        costume_assembly_transcriber,
        'do_get_request',
        return_value=(200, mock_response)
    )

    await costume_assembly_transcriber.async_get_transcript(costume_assembly_transcriber.client, transcript_id)

    mock_do_get.assert_called_once_with(
        client=costume_assembly_transcriber.client,
        url=f"{ENDPOINT_TRANSCRIPT}/{transcript_id}"
    )


class TestCreateTranscriptObj:
    url = "http://example.com/audio.mp3"
    language_code = 'ru'

    def test_create_transcript_obj_valid(self, costume_assembly_transcriber):
        transcript_request = costume_assembly_transcriber.create_transcript_obj(self.url)

        assert isinstance(transcript_request, TranscriptRequest)
        assert transcript_request.audio_url == self.url


@pytest.mark.asyncio
async def test_async_wait_for_completion_success(costume_assembly_transcriber, mocker):
    mock_transcript = TranscriptResponse(audio_url="123", id="123", status="completed")
    mocker.patch.object(costume_assembly_transcriber, 'async_get_transcript', return_value=mock_transcript)

    input_response = TranscriptResponse(audio_url="123", id="123", status="processing")

    result = await costume_assembly_transcriber.async_wait_for_completion(
        costume_assembly_transcriber.client,
        input_response
    )

    assert result == mock_transcript
    costume_assembly_transcriber.async_get_transcript.assert_called_with(
        client=costume_assembly_transcriber.client,
        transcript_id="123"
    )


@pytest.mark.asyncio
async def test_async_wait_for_completion_api_error(costume_assembly_transcriber, mocker):
    mock_transcript = TranscriptResponse(audio_url="123", id="123", status="error")
    mock_async_get = mocker.patch.object(
        costume_assembly_transcriber, 'async_get_transcript', return_value=mock_transcript
    )

    input_response = TranscriptResponse(audio_url="123", id="123", status="processing")

    with pytest.raises(RetryError) as exc_info:
        await costume_assembly_transcriber.async_wait_for_completion(
            costume_assembly_transcriber.client,
            input_response
        )

        assert isinstance(exc_info.value.last_attempt.exception(), APITranscriptionError)
        assert mock_async_get.call_count == 3

    mock_async_get.assert_called_with(client=costume_assembly_transcriber.client, transcript_id="123")


@pytest.mark.asyncio
async def test_async_wait_for_completion_unknown_error(costume_assembly_transcriber, mocker):
    mocker.patch.object(costume_assembly_transcriber, 'async_get_transcript', side_effect=Exception("Unexpected error"))

    input_response = TranscriptResponse(audio_url="123", id="123", status="processing")

    with pytest.raises(RetryError) as exc_info:
        await costume_assembly_transcriber.async_wait_for_completion(
            costume_assembly_transcriber.client,
            input_response
        )

        assert isinstance(exc_info.value.last_attempt.exception(), UnknownTranscriptionError)

        assert "Non-API error occurred" in str(exc_info.value)
    costume_assembly_transcriber.async_get_transcript.assert_called_with(
        client=costume_assembly_transcriber.client,
        transcript_id="123"
    )


@pytest.mark.asyncio
async def test_async_wait_for_completion_retries(costume_assembly_transcriber, mocker):
    mock_transcript_in_progress = TranscriptResponse(audio_url="123", id="123", status="processing")
    mock_transcript_completed = TranscriptResponse(audio_url="123", id="123", status="completed")

    mocker.patch.object(costume_assembly_transcriber, 'async_get_transcript', side_effect=[
        mock_transcript_in_progress, mock_transcript_in_progress, mock_transcript_completed
    ])

    input_response = TranscriptResponse(audio_url="123", id="123", status="processing")

    result = await costume_assembly_transcriber.async_wait_for_completion(
        costume_assembly_transcriber.client,
        input_response
    )

    assert result == mock_transcript_completed
    assert costume_assembly_transcriber.async_get_transcript.call_count == 3


@pytest.mark.asyncio
class TestTranscriber:
    async def test_transcribe_success(
            self,
            costume_assembly_transcriber,
            get_costume_assembly_transcriber_client,
            mocker
    ):
        mock_client = await get_costume_assembly_transcriber_client

        mock_file_url = "http://example.com/audio.mp3"
        mock_transcript_request = "mock_transcript_request"
        mock_transcript = "mock_transcript"
        mock_response = "final_transcript"

        mocker.patch.object(costume_assembly_transcriber, 'async_upload_file', return_value=mock_file_url)
        mocker.patch.object(costume_assembly_transcriber, 'create_transcript_obj', return_value=mock_transcript_request)
        mocker.patch.object(costume_assembly_transcriber, 'async_create_transcript', return_value=mock_transcript)
        mocker.patch.object(costume_assembly_transcriber, 'async_wait_for_completion', return_value=mock_response)
        mock_from_text = mocker.patch(
            "src.consumption.consumers.transcriber.from_text",
            return_value="transcription_result"
        )
        mocker.patch.object(costume_assembly_transcriber.client, 'create_client', return_value=mock_client)

        result = await costume_assembly_transcriber.transcribe(file_path="test_file.mp3")

        assert result == "transcription_result"
        costume_assembly_transcriber.async_upload_file.assert_called_with(
            client=mock_client,
            file_path="test_file.mp3"
        )
        costume_assembly_transcriber.create_transcript_obj.assert_called_with(mock_file_url)
        costume_assembly_transcriber.async_create_transcript.assert_called_with(
            client=mock_client,
            request=mock_transcript_request
        )
        costume_assembly_transcriber.async_wait_for_completion.assert_called_with(
            client=mock_client,
            transcript_response=mock_transcript
        )
        mock_from_text.assert_called_with(response=mock_response)

    async def test_transcribe_upload_error(
            self,
            costume_assembly_transcriber,
            get_costume_assembly_transcriber_client,
            mocker
    ):
        mock_client = await get_costume_assembly_transcriber_client
        mocker.patch.object(
            costume_assembly_transcriber,
            'async_upload_file',
            side_effect=TranscriptError("Upload failed")
        )
        mocker.patch.object(costume_assembly_transcriber.client, 'create_client', return_value=mock_client)

        with pytest.raises(TranscriptError) as exc_info:
            await costume_assembly_transcriber.transcribe(file_path="test_file.mp3")

        assert str(exc_info.value) == "Upload failed"
        costume_assembly_transcriber.async_upload_file.assert_called_with(client=mock_client, file_path="test_file.mp3")

    async def test_transcribe_wait_for_completion_error(
            self,
            costume_assembly_transcriber,
            get_costume_assembly_transcriber_client,
            mocker
    ):
        mock_client = await get_costume_assembly_transcriber_client
        mock_file_url = "http://example.com/audio.mp3"
        mock_transcript_request = "mock_transcript_request"
        mock_transcript = "mock_transcript"

        mocker.patch.object(costume_assembly_transcriber.client, 'create_client', return_value=mock_client)
        mocker.patch.object(costume_assembly_transcriber, 'async_upload_file', return_value=mock_file_url)
        mocker.patch.object(costume_assembly_transcriber, 'create_transcript_obj', return_value=mock_transcript_request)
        mocker.patch.object(costume_assembly_transcriber, 'async_create_transcript', return_value=mock_transcript)
        mocker.patch.object(
            costume_assembly_transcriber,
            'async_wait_for_completion',
            side_effect=APITranscriptionError("Completion error")
        )

        # Проверка на выброс ошибки
        with pytest.raises(APITranscriptionError) as exc_info:
            await costume_assembly_transcriber.transcribe(file_path="test_file.mp3")

        assert "Completion error" in str(exc_info.value)
        costume_assembly_transcriber.async_upload_file.assert_called_with(client=mock_client, file_path="test_file.mp3")
        costume_assembly_transcriber.create_transcript_obj.assert_called_with(mock_file_url)
        costume_assembly_transcriber.async_create_transcript.assert_called_with(
            client=mock_client,
            request=mock_transcript_request
        )
        costume_assembly_transcriber.async_wait_for_completion.assert_called_with(
            client=mock_client,
            transcript_response=mock_transcript
        )


# =================AsyncWrappedAssemblyTranscriber====================
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