import asyncio
import os

from aiogram.client.session import aiohttp

from src.file_manager.interface import IBaseFileLoader


class S3FileLoader(IBaseFileLoader):
    def __init__(self, s3_url):
        self.s3_url: str = s3_url

    async def load(self) -> str:
        current_directory = os.getcwd()  # Получаем текущую директорию
        destination_filename = os.path.join(current_directory, self.s3_url.split('/')[-1])  # получение имени файла
        await self.download_file_from_url(self.s3_url, destination_path=destination_filename)

        return destination_filename

    @staticmethod
    async def download_file_from_url(url: str, destination_path: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(destination_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                print(f"File downloaded to {destination_path}")

    async def __call__(self, *args, **kwargs):
        return await self.load()


async def main():
    file_loader = S3FileLoader(
        'https://b8ffac09-9e42-4827-b4b2-22f1081ea55c.selstorage.ru/posting-label-58515541-0006-2.pdf')
    await file_loader.load()


if __name__ == '__main__':
    asyncio.run(main())
