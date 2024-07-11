import contextlib
import sys

import assemblyai
import assemblyai as aai
import aiohttp
from aiohttp import ClientTimeout, ClientSession


class AssemblyClient:

    def __init__(self, api_key):
        aai.settings.api_key = api_key
        self.TranscriptionConfig = aai.TranscriptionConfig
        self.Transcriber = aai.Transcriber


class AsyncAssemblyClient:
    base_url: str = "https://api.assemblyai.com"
    version = "0.28.1"
    http_timeout: float = 30 * 60

    def __init__(self, api_key):
        self.api_key = api_key

    @contextlib.asynccontextmanager
    async def create_client(self) -> aiohttp.ClientSession:
        vi = sys.version_info
        python_version = f"{vi.major}.{vi.minor}.{vi.micro}"
        user_agent = f"AiohttpClient/1.0 (sdk=Python/{python_version} runtime_env=Python/{python_version})"

        headers = {
            "user-agent": user_agent,
            "authorization": self.api_key
        }

        session = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=headers,
            timeout=ClientTimeout(total=self.http_timeout)
        )
        try:
            yield session
        finally:
            await session.close()
