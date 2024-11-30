from src.consumption.consumers.interface import ISummarizer
from src.consumption.exeptions.summarize import NoResponseFromChatGptSummarization
from src.consumption.models.consumption.asssistant import AIAssistant
from src.services.openai_api_package.chat_gpt_package.client import GPTClient
from src.services.openai_api_package.chat_gpt_package.model import GPTMessage, GPTRole


class GptSummarizer(ISummarizer):

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    async def summarize(self, transcribed_text: str, assistant: AIAssistant) -> str:
        try:
            user_message = GPTMessage(role=GPTRole.USER, content=assistant.user_prompt + transcribed_text)
            system_message = GPTMessage(role=GPTRole.SYSTEM, content=assistant.assistant_prompt)
            return await self.gpt_client.complete(user_message, system_message)

        except Exception as e:
            raise NoResponseFromChatGptSummarization(
                f'Произошла ошибка: не удалось выполнить суммаризацию с помощью ChatGPT.\n'
                f'{str(e)}'
            )

    async def __call__(self, transcribed_text: str, assistant: AIAssistant) -> str:
        return await self.summarize(transcribed_text, assistant)
