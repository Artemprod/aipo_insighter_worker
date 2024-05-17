import asyncio
import os
import time
from functools import wraps
from multiprocessing import cpu_count

import aiofiles
from pydub import AudioSegment
from pydub.utils import make_chunks

from abc import ABC, abstractmethod


class BaseCropper(ABC):

    def __init__(self, chunk_lents_seconds: int,
                 output_path:str):
        self.chunk_length_seconds = chunk_lents_seconds
        self.output_path=output_path

    @abstractmethod
    async def crop_file(self, *args, **kwargs):
        pass


class SyncCropper(BaseCropper):

    async def crop_file(self, file_path):
        paths = []
        duration = self.chunk_length_seconds * 1000
        sound = AudioSegment.from_file(file_path)
        for i, chunk in enumerate(sound[::duration]):
            save_path = fr"{self.output_path}\chunk_{i}.mp3"
            with open(save_path, "wb") as f:
                chunk.export(f, format="mp3")
                paths.append(save_path)
        return paths

    async def __call__(self, file_path, output_path):
        return self.crop_file(file_path, output_path)


class AsyncCropper(BaseCropper):

    async def crop_file(self, file_path, max_concurrent_tasks=None):
        paths = []
        duration = self.chunk_length_seconds * 1000
        sound = AudioSegment.from_file(file_path)
        chunks = make_chunks(sound, duration)

        if max_concurrent_tasks is None:
            max_concurrent_tasks = cpu_count()

        semaphore = asyncio.Semaphore(max_concurrent_tasks)

        tasks = []
        for i, chunk in enumerate(chunks):
            save_path = os.path.normpath(os.path.join(self.output_path, f"chunk_{i}.mp3"))
            tasks.append(self.export_chunk(chunk, save_path, semaphore))
            paths.append(save_path)

        await asyncio.gather(*tasks)
        return paths

    @staticmethod
    async def export_chunk(chunk, save_path, semaphore):
        async with semaphore:
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(chunk.export(format="mp3").read())
                print(save_path)

    async def __call__(self, file_path, max_concurrent_tasks=None):
        return await self.crop_file(file_path, max_concurrent_tasks)


if __name__ == '__main__':
    as_croper = AsyncCropper(chunk_lents_seconds=60 * 10)
    o_p = r'D:\projects\AIPO_V2\insighter_worker\temp'
    asyncio.run(as_croper(r"C:\Users\artem\OneDrive\Рабочий стол\Тестовые данные\M4A.m4a",
                          output_path=o_p))
