from aiogram.client.session import aiohttp
from loguru import logger
from pathlib import Path

from src.file_manager.exceptions.s3 import  S3FileNotDownloaded
from src.file_manager.base_file_manager import BaseFileManager
from src.utils.utils_exceptions import NoPath


class S3FileManager(BaseFileManager):
    def __init__(self):
        pass

    async def _load(self, url: str, output_path: str) -> str:
        await self.download_file_from_url(url, destination_path=output_path)
        return output_path

    @staticmethod
    async def download_file_from_url(url: str, destination_path: str) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    with open(destination_path, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                    logger.info(f"File downloaded to {destination_path}")
        except Exception as e:
            raise S3FileNotDownloaded(url=url, exception_info=e)

    def _extract_file_name_from_url(self, url: str) -> str | None:
        if not url:
            raise NoPath('Не удалось извлечь путь до файла')
        clean_path = url.split('?')[0]
        file_name = Path(clean_path).name
        return file_name
