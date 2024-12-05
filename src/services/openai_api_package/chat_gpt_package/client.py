import asyncio

from aiohttp import ClientSession, ClientTimeout

from src.services.openai_api_package.chat_gpt_package.model import GPTOptions


class GPTClient:

    def __init__(self, *, options: GPTOptions):
        self.options = options
        self._lock = asyncio.Lock()

    async def complete(self, user_message: str, system_message: str) -> str:
        async with self._lock:
            user_request = {
                "user_prompt": user_message,
                "system_prompt": system_message
            }
            return await self._request(user_request)

    async def _request(self, gpt_args: dict) -> str:
        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            try:
                async with session.post(self.options.openai_url_single_request, json=gpt_args) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data.get("response", "")
                    raise Exception(f"Error: {response.status}, {await response.text()}")
            except asyncio.TimeoutError as ex:
                raise Exception(f"Timeout error: {ex}")
