import os
import re
import shutil
import tempfile
from pathlib import Path


from loguru import logger

from src.utils.utils_exceptions import NoPath, NoYoutubeUrl


def create_s3_file_name(path: str) -> str:
    """
    Generate file name from the provided path.

    :param path: The full path to the file.
    :return: The extracted file name.
    :raises ValueError: If the path is empty.
    """

    if not path:
        raise NoPath(path)
    clean_path = path.split('?')[0]
    file_name = Path(clean_path).name
    return file_name

def create_youtube_file_name(youtube_url: str) -> str:
    """
    Generate file name from the provided url.

    :param path: The full path to the file.
    :return: The extracted file name.
    :raises ValueError: If the path is empty.
    """

    if not youtube_url:
        raise NoYoutubeUrl(youtube_url)
    return youtube_url.split('/')[-1]


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
    if Path(path).is_file():
        path = Path(path).parent
    shutil.rmtree(path, ignore_errors=True)
    logger.info(f"Временная директория удалена: {path}")


def is_youtube_url(url) -> bool:
    # Шаблоны URL, которые поддерживают список видео, короткие ссылки и стандартные ссылки
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'  # YouTube видео всегда имеют 11-значный ID
    )

    return bool(re.match(youtube_regex, url))
