import random
import shutil
import string
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from loguru import logger

from src.pipelines.models import PiplineData


# Базовый класс для операций с файлами
class BaseFileManager(ABC):
    async def start_load(self, pipeline_data: PiplineData) -> str:
        output_path =  self._create_temp_file_path(pipeline_data)
        return await self._load(url=pipeline_data.file_destination, output_path=output_path)

    def _create_temp_file_path(self, pipeline_data: PiplineData) -> str:
        file_name = self._extract_file_name_from_url(url=pipeline_data.file_destination)
        temp_file_path = self._create_temp_directory(file_name=file_name, user_id=pipeline_data.initiator_user_id)
        return temp_file_path

    @staticmethod
    def _generate_random_file_name(length: int = 10) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def _create_temp_directory(file_name: str | None, user_id: int) -> str:
        logger.info("создаю временную директорию ...")
        user_id = str(user_id)
        temp_dir = Path(tempfile.mkdtemp())
        user_dir = temp_dir / user_id
        temp_file_path = user_dir / file_name if file_name else user_dir
        temp_file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"временная директория {temp_file_path}")
        return str(temp_file_path)

    @staticmethod
    def clear_temp_directory(path: str | None):
        """
        Удаляет временную директорию и все файлы в ней.
        """
        if not path:
            return
        if Path(path).is_file():
            path = Path(path).parent
        shutil.rmtree(path, ignore_errors=True)
        logger.info(f"Временная директория удалена: {path}")

    @abstractmethod
    def _extract_file_name_from_url(self, url: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def _load(self, url: str, output_path: str) -> str:
        raise NotImplementedError
