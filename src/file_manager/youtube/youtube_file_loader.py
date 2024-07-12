import os
import re

from loguru import logger
from pytube import YouTube
from yt_dlp import YoutubeDL

from src.file_manager.exceptions.youtube_loader import YoutubeAudioNotDownloaded
from src.file_manager.interface import IBaseFileLoader
from src.utils.wrappers import async_wrap


class YouTubeFileLoader(IBaseFileLoader):

    @async_wrap
    def load(self, youtube_url, output_path):
        try:
            yt = YouTube(youtube_url)
            audio_stream = yt.streams.get_audio_only()
            output_file = audio_stream.download(output_path=output_path)
        except Exception as e:
            raise YoutubeAudioNotDownloaded(url=youtube_url, exception_info=e) from e
        else:
            return os.path.normpath(output_file)

    async def __call__(self, youtube_url, output_path) -> str:
        return await self.load(youtube_url, output_path)


class DLYouTubeFileLoader(IBaseFileLoader):

    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    def download_audio(self, url, output_path):
        ydl_opts = self.ydl_opts.copy()
        ydl_opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'requested_downloads' in info:
                downloaded_file = info['requested_downloads'][0]['filepath']
                return downloaded_file
            else:
                raise YoutubeAudioNotDownloaded(url, "Download failed")

    @async_wrap
    def load(self, youtube_url, output_path):
        try:
            output_file = self.download_audio(youtube_url, output_path)
        except Exception as e:
            raise YoutubeAudioNotDownloaded(url=youtube_url, exception_info=e) from e
        else:
            return os.path.normpath(output_file)

    async def __call__(self, youtube_url, output_path) -> str:
        return await self.load(youtube_url, output_path)
