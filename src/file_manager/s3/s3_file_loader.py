import asyncio
import os

from aiogram.client.session import aiohttp

from src.file_manager.interface import IBaseFileLoader


class S3FileLoader(IBaseFileLoader):
    def __init__(self):
        pass

    async def load(self, s3_url, destination_directory: str) -> str:
        await self.download_file_from_url(s3_url, destination_path=destination_directory)
        return destination_directory

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

    async def __call__(self, s3_url, destination_directory: str):
        return await self.load(s3_url, destination_directory)


# async def main():
#     file_loader = S3FileLoader(
#         'https://b8ffac09-9e42-4827-b4b2-22f1081ea55c.selstorage.ru/posting-label-58515541-0006-2.pdf')
#     await file_loader.load()


# if __name__ == '__main__':
#     asyncio.run(main())
