import pytest

from src.consumption.consumers.transcriber import AssemblyTranscriber


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
    result = await assembly_transcriber("path/to/file.mp4")
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
