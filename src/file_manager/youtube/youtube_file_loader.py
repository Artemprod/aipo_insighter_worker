import asyncio
import os
from functools import wraps, partial

from pytube import YouTube

from src.file_manager.base_file_loader import  BaseFileLoader
from src.utils.wrappers import async_wrap


class YouTubeFileLoader(BaseFileLoader):
 #TODO в классе в ините настройки поведения всего класса независимие от контрактов всякие timaut, кодек и тп
    def __init__(self,youtube_url, path):
        self.youtube_url = youtube_url
        self.path = path

 # TODO а здесь уже контракты
    @async_wrap
    def load(self):
        yt = YouTube(self.youtube_url)
        audio_stream = yt.streams.get_audio_only()
        output_file = audio_stream.download(output_path=self.path )
        return os.path.normpath(output_file)

    async def __call__(self):
        return await self.load()



