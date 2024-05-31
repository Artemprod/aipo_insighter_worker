import os

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import Message

from src.exceptions.format_exceptions import TelegramCantFindFileError
from src.file_manager.telegram_server_back.base_file_manager import IMediaFileManager
from src.utils.logger import insighter_logger


class MediaFileManager(IMediaFileManager):
    base_path = "/var/lib/telegram-bot-api"

    async def get_media_file(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    async def get_file_id_from_message(message: Message) -> str:
        content_type_to_file_id_attr = {
            ContentType.VOICE: "voice",
            ContentType.AUDIO: "audio",
            ContentType.DOCUMENT: "document",
            ContentType.VIDEO: "video",
        }

        file_id_attr = content_type_to_file_id_attr.get(message.content_type)
        return getattr(message, file_id_attr, None).file_id if file_id_attr else None

    @staticmethod
    async def get_shared_file_path(message: Message, file, bot: Bot) -> str:
        content_type_to_folder = {
            ContentType.VIDEO: "videos",
            ContentType.VOICE: "voice",
            ContentType.AUDIO: "music",
            ContentType.DOCUMENT: "documents",
        }

        folder_name = content_type_to_folder.get(message.content_type, "")
        return os.path.join(
            MediaFileManager.base_path,
            bot.token,
            folder_name,
            os.path.basename(file.file_path),
        )

    async def get_file(self, message: Message, bot: Bot) -> Bot:
        file_id = await self.get_file_id_from_message(message)
        if file_id is None:
            raise TelegramCantFindFileError("File can't be found in the existing file system")
        return await bot.get_file(file_id)

    @staticmethod
    def log_file_info(level, message, file_path=None, error_msg=None):
        user_info = (
            f"id: {message.chat.id}, "
            f"first name: {message.from_user.first_name}, "
            f"last name: {message.from_user.last_name}"
        )

        if level == "info":
            insighter_logger.info(f"File for {user_info} located in {file_path}")
        elif level == "error":
            insighter_logger.exception(f"Error for {user_info}: {error_msg}")
