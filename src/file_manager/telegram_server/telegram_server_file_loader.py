import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import paramiko
from aiogram import Bot
from aiogram.types import Message
from environs import Env

import container
from src.exceptions.path_exceptions import (
    TelegramServerFileCantBeFoundError,
    TelegramServerVolumePathExistingError,
)
from src.utils.logger import insighter_logger
from .media_file_manager import MediaFileManager


class TelegramMediaFileManager(MediaFileManager):
    async def get_media_file(self, message: Message, bot: Bot):
        try:
            result = await self.get_file_path(message, bot)
            self.log_file_info("info", message, result)
            return result
        except TelegramServerVolumePathExistingError as e:
            self.log_file_info(
                "error",
                message,
                None,
                "File hasn't been found in common docker volume",
            )
            raise TelegramServerFileCantBeFoundError("File hasn't been found in common docker volume") from e

    async def get_file_path(self, message: Message, bot: Bot) -> str:
        file = await self.get_file(message, bot)
        shared_file_path = await self.get_shared_file_path(message, file, bot)
        return await self._check_and_return_path(shared_file_path)

    @staticmethod
    async def _check_and_return_path(file_path) -> str:
        if await asyncio.to_thread(os.path.exists, file_path):
            insighter_logger.info(f"File found in the existing file system. File path is: {file_path}")
            return file_path
        else:
            raise TelegramServerVolumePathExistingError(
                f"File, supposedly located in:{file_path}, hasn't been found in common docker volume"
            )


class ServerFileManager(MediaFileManager):
    local_file_path = r"D:\projects\AIPO\insighter_ai\insighter\main_process\temp"

    @dataclass
    class Configs:
        hostname: str
        username: str
        password: str

    @dataclass
    class Filepaths:
        audio: str
        video: str
        documents: str
        voice: str

    def __init__(self):
        self.file_paths = self.create_file_paths()

    @classmethod
    def __bot_token(cls):
        if container.system == "local":
            return container.test_telegram_bot_token
        elif container.system == "docker":
            return container.telegram_bot_token

    async def get_media_file(self, message: Message, bot: Bot) -> str:
        remote_file_path = await self.get_file(message, bot)

        loop = asyncio.get_event_loop()

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
            result = await loop.run_in_executor(
                pool,
                self.download_file,
                remote_file_path.file_path,
            )
        return result

    def create_file_paths(self) -> Filepaths:
        token = self.__bot_token()
        video = f"/var/lib/docker/volumes/insighter_ai_shared_volume/_data/{token}/videos/"
        audio = f"/var/lib/docker/volumes/insighter_ai_shared_volume/_data/{token}/music/"
        documents = f"/var/lib/docker/volumes/insighter_ai_shared_volume/_data/{token}/documents/"
        voice = f"/var/lib/docker/volumes/insighter_ai_shared_volume/_data/{token}/voice/"
        return ServerFileManager.Filepaths(audio=audio, video=video, documents=documents, voice=voice)

    @classmethod
    def __load_config(cls) -> Configs:
        env: Env = Env()
        env.read_env(".env")
        return cls.Configs(
            hostname=env('REMOTE_SERVER_HOST'),
            username=env('REMOTE_SERVER_USER_NAME'),
            password=env('REMOTE_SERVER_PASSWORD')
        )

    def __connect_server(self):
        server_configs = self.__load_config()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=server_configs.hostname,
                username=server_configs.username,
                password=server_configs.password,
            )
            return client
        except Exception as e:
            insighter_logger.info("Ошибка подключения сервера", e)

    def list_files_in_directory(self, directory_path):
        client = self.__connect_server()
        try:
            # Команда для получения списка файлов в директории
            stdin, stdout, stderr = client.exec_command(f'ls "{directory_path}"')
            files = stdout.read().decode().splitlines()

            return files
        except Exception as e:
            insighter_logger.info(f"Ошибка при получении списка файлов: {e}")
            return None
        finally:
            client.close()

    def check_file_exists(self, income_file_path):
        client = self.__connect_server()

        income_format = self.__define_type(income_file_path)
        file_name = self.get_file_name(income_file_path)
        path = None
        if income_format == "music":
            path = f"{self.file_paths.audio}{file_name}"
        elif income_format == "videos":
            path = f"{self.file_paths.video}{file_name}"
        elif income_format == "documents":
            path = f"{self.file_paths.documents}{file_name}"
        elif income_format == "voice":
            path = f"{self.file_paths.voice}{file_name}"
        try:
            # Команда для проверки файла

            stdin, stdout, stderr = client.exec_command(f'test -f "{path}" && echo exists || echo not exists')
            result = stdout.read().decode().strip()

            return result == "exists"
        except Exception as e:
            insighter_logger.info(f"Ошибка подключения: {e}")
            return False
        finally:
            client.close()

    def __execute_command_get_remote_file_size_mb(self, file_path):
        client = self.__connect_server()
        try:
            # Команда для получения размера файла
            command = f'stat -c%s "{file_path}"'
            stdin, stdout, stderr = client.exec_command(command)
            size_bytes = int(stdout.read().decode().strip())

            size_mb = size_bytes / (1024 * 1024)  # Преобразование из байтов в мегабайты
            return size_mb
        except Exception as e:
            insighter_logger.info(f"Ошибка: {e}")
            return None
        finally:
            client.close()

    def download_file(
            self,
            remote_file_path,
    ):
        client = self.__connect_server()

        income_format = self.__define_type(remote_file_path)
        file_name = self.get_file_name(remote_file_path)
        server_file_path = None
        if income_format == "music":
            server_file_path = f"{self.file_paths.audio}{file_name}"
        elif income_format == "videos":
            server_file_path = f"{self.file_paths.video}{file_name}"
        elif income_format == "documents":
            server_file_path = f"{self.file_paths.documents}{file_name}"
        elif income_format == "voice":
            server_file_path = f"{self.file_paths.voice}{file_name}"

        try:
            local_file_path = ServerFileManager.local_file_path
            local_file_full_path = os.path.join(local_file_path, file_name)
            sftp = client.open_sftp()
            sftp.get(server_file_path, local_file_full_path)
            sftp.close()
            return local_file_full_path
        except Exception as e:
            insighter_logger.exception(e)
            insighter_logger.info(f"Ошибка при загрузке файла: {e}")
            return None
        finally:
            client.close()

    def get_server_file_size(self, income_file_path):
        income_format = self.__define_type(income_file_path)
        file_name = self.get_file_name(income_file_path)
        size_mb = None
        if income_format == "music":
            size_mb = self.__execute_command_get_remote_file_size_mb(file_path=f"{self.file_paths.audio}{file_name}")
        elif income_format == "videos":
            size_mb = self.__execute_command_get_remote_file_size_mb(file_path=f"{self.file_paths.video}{file_name}")
        elif income_format == "documents":
            size_mb = self.__execute_command_get_remote_file_size_mb(
                file_path=f"{self.file_paths.documents}{file_name}"
            )
        elif income_format == "voice":
            size_mb = self.__execute_command_get_remote_file_size_mb(file_path=f"{self.file_paths.voice}{file_name}")
        return size_mb

    def delete_file(self, income_file_path):
        client = self.__connect_server()
        income_format = self.__define_type(income_file_path)
        file_name = self.get_file_name(income_file_path)
        path = None
        if income_format == "music":
            path = f"{self.file_paths.audio}{file_name}"
        elif income_format == "videos":
            path = f"{self.file_paths.video}{file_name}"
        elif income_format == "documents":
            path = f"{self.file_paths.documents}{file_name}"
        elif income_format == "voice":
            path = f"{self.file_paths.voice}{file_name}"

        try:
            # Команда для удаления файла
            stdin, stdout, stderr = client.exec_command(f'rm "{path}"')
            stderr_result = stderr.read().decode().strip()

            if stderr_result:
                insighter_logger.info(f"Ошибка при удалении файла: {stderr_result}")
                return False
            else:
                insighter_logger.info(f"Файл успешно удален: {path}")
                return True
        except Exception as e:
            insighter_logger.info(f"Ошибка подключения: {e}")
            return False
        finally:
            client.close()

    @staticmethod
    def __define_type(path: str):
        parts = path.split("/")
        format_type = parts[-2]
        return format_type

    @staticmethod
    def get_file_name(path: str):
        parts = path.split("/")
        file_name = parts[-1]
        return file_name
