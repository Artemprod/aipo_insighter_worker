from src.consumption.consumers.interface import ISummarizer
from src.consumption.exeptions.summarize import NoResponseFromChatGptSummarization
from src.consumption.models.consumption.asssistant import AIAssistantScheme
from src.services.openai_api_package.chat_gpt_package.client import GPTClient


class GptSummarizer(ISummarizer):

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    async def summarize(self, transcribed_text: str, assistant: AIAssistantScheme) -> str:
        try:
            return await self.gpt_client.complete(
                user_message=f'{assistant.user_prompt} {transcribed_text}',
                system_message=assistant.assistant_prompt
            )

        except Exception as e:
            raise NoResponseFromChatGptSummarization(
                f'Произошла ошибка: не удалось выполнить суммаризацию с помощью ChatGPT.\n'
                f'{str(e)}'
            )

    async def __call__(self, transcribed_text: str, assistant: AIAssistantScheme) -> str:
        return await self.summarize(transcribed_text, assistant)
