import os
from pytube import YouTube
from src.file_manager.interface import IBaseFileLoader
from src.utils.wrappers import async_wrap


class YouTubeFileLoader(IBaseFileLoader):

    @async_wrap
    def load(self, youtube_url, output_path):
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.get_audio_only()
        output_file = audio_stream.download(output_path=output_path)
        return os.path.normpath(output_file)
