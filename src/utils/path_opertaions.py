import random
import re
import shutil
import string
import tempfile
from pathlib import Path


from loguru import logger

from src.utils.utils_exceptions import NoPath, NoYoutubeUrl


class FileNameExtractor:
    @classmethod
    def extract_file_name_from_url(cls, url: str) -> str:
        file_name = None

        if cls.is_youtube_url(url):
            file_name = cls.create_youtube_file_name(url)
        elif cls.is_google_drive_url(url):
            file_name = cls.create_google_drive_file_name(url)
        elif cls.is_s3_url(url):
            file_name = cls.create_s3_file_name(url)

        # Проверка URL производится на боте
        if file_name is None:
            file_name = cls.generate_random_file_name()

        return file_name

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(re.match(youtube_regex, url))

    @staticmethod
    def is_google_drive_url(url: str) -> bool:
        return "drive.google.com" in url

    @staticmethod
    def is_s3_url(url: str) -> bool:
        return "s3.amazonaws.com" in url or "s3." in url

    @staticmethod
    def create_s3_file_name(path: str) -> str:
        if not path:
            raise NoPath('Не удалось извлечь путь до файла')
        clean_path = path.split('?')[0]
        file_name = Path(clean_path).name
        return file_name

    @staticmethod
    def create_youtube_file_name(youtube_url: str) -> str:
        if not youtube_url:
            raise NoPath('Не удалось извлечь путь до файла')
        return youtube_url.split('/')[-1]

    @staticmethod
    def create_google_drive_file_name(drive_url: str) -> str:
        pattern = r"(?:/d/|uc\?id=)([a-zA-Z0-9_-]+)"
        match = re.search(pattern, drive_url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def generate_random_file_name(length: int = 10) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


def create_temp_path(file_name: str | None, user_id: int) -> str:
    logger.info("создаю временную директорию ...")
    user_id = str(user_id)
    temp_dir = Path(tempfile.mkdtemp())
    user_dir = temp_dir / user_id
    temp_file_path = user_dir / file_name if file_name else user_dir
    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"временная директория {temp_file_path}")
    return str(temp_file_path)


def clear_temp_dir(path: str):
    """
    Удаляет временную директорию и все файлы в ней.
    """
    if not path:
        return
    if Path(path).is_file():
        path = Path(path).parent
    shutil.rmtree(path, ignore_errors=True)
    logger.info(f"Временная директория удалена: {path}")
