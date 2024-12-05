from dataclasses import dataclass

import pytest

from src.consumption.consumers.summarizer import GptSummarizer
from src.consumption.models.consumption.asssistant import AIAssistantScheme
from src.services.openai_api_package.chat_gpt_package.client import GPTClient


@dataclass
class TestDataCase:
    transcribed_text: str
    expected_response: str


TEST_CASES = [
    TestDataCase(transcribed_text="This is a transcribed text.", expected_response="This is a summary."),
    TestDataCase(transcribed_text="", expected_response=""),
    TestDataCase(transcribed_text="Another transcribed text.", expected_response="Another summary."),
]


@pytest.fixture
def mock_gpt_client(mocker):
    return mocker.Mock(spec=GPTClient)


@pytest.fixture
def gpt_summarizer(mock_gpt_client):
    return GptSummarizer(gpt_client=mock_gpt_client)


@pytest.fixture
def assistant():
    return AIAssistantScheme(
        assistant="test_assistant",
        name="Test Assistant",
        assistant_prompt="Test assistant prompt",
        user_prompt="Test user prompt"
    )


class TestGptSummarizer:
    @classmethod
    def pytest_generate_tests(cls, metafunc):
        if "test_case" in metafunc.fixturenames:
            metafunc.parametrize(
                "test_case",
                [
                    pytest.param(test_case, id=f"transcribed_text_{test_case.transcribed_text}")
                    for test_case in TEST_CASES
                ]
            )

    @pytest.mark.asyncio
    async def test_summarize_calls_gpt_client(self, gpt_summarizer, mock_gpt_client, assistant, mocker, test_case):
        mock_gpt_client.complete = mocker.AsyncMock(return_value=test_case.expected_response)
        user_message = assistant.user_prompt + test_case.transcribed_text
        system_message = assistant.assistant_prompt

        result = await gpt_summarizer.summarize(test_case.transcribed_text, assistant)

        mock_gpt_client.complete.assert_called_once_with(user_message=user_message, system_message=system_message)
        assert result == test_case.expected_response

    @pytest.mark.asyncio
    async def test_call_invokes_summarize(self, gpt_summarizer, assistant, mocker, test_case):
        gpt_summarizer.summarize = mocker.AsyncMock(return_value=test_case.expected_response)

        result = await gpt_summarizer(test_case.transcribed_text, assistant)

        gpt_summarizer.summarize.assert_called_once_with(test_case.transcribed_text, assistant)
        assert result == test_case.expected_response

    @pytest.mark.asyncio
    async def test_summarize_with_empty_text(self, gpt_summarizer, mock_gpt_client, assistant, mocker, test_case):
        mock_gpt_client.complete = mocker.AsyncMock(return_value=test_case.expected_response)

        result = await gpt_summarizer.summarize(test_case.transcribed_text, assistant)

        assert result == test_case.expected_response
        mock_gpt_client.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_summarize_handles_unexpected_response(self, gpt_summarizer, mock_gpt_client, assistant, mocker, test_case):
        mock_gpt_client.complete = mocker.AsyncMock(return_value=None)

        result = await gpt_summarizer.summarize(test_case.transcribed_text, assistant)

        assert result is None
        mock_gpt_client.complete.assert_called_once()
