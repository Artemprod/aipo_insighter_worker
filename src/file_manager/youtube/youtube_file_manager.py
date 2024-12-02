import os

from pytube import YouTube
from yt_dlp import YoutubeDL

from src.file_manager.exceptions.youtube_loader import YoutubeAudioNotDownloaded
from src.file_manager.base_file_manager import BaseFileManager
from src.file_manager.types import FilePath
from src.utils.utils_exceptions import NoPath
from src.utils.wrappers import async_wrap


class YouTubeFileManager(BaseFileManager):

    @async_wrap
    def _load(self, url: str, output_path: str) -> FilePath:
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.get_audio_only()
            output_file = audio_stream.download(output_path=output_path)
        except Exception:
            raise YoutubeAudioNotDownloaded(url, "Произошла ошибка: не удалось скачать аудио с YouTube.")
        else:
            return os.path.normpath(output_file)

    def _extract_file_name_from_url(self, url: str) -> str:
        if not str:
            raise NoPath('Не удалось извлечь путь до файла')
        return str.split('/')[-1]


class DLYouTubeFileManager(BaseFileManager):

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
    def _load(self, url: str, output_path: str) -> FilePath:
        try:
            output_file = self.download_audio(url, output_path)
        except Exception:
            raise YoutubeAudioNotDownloaded(url, "Произошла ошибка: не удалось скачать аудио с YouTube")
        else:
            return os.path.normpath(output_file)

    def _extract_file_name_from_url(self, url: str) -> str | None:
        if not url:
            raise NoPath('Не удалось извлечь путь до файла')
        return url.split('/')[-1]
