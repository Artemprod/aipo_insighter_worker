from abc import ABC, abstractmethod


class IMediaFileManager(ABC):
    @abstractmethod
    async def get_media_file(self, *args, **kwargs) -> str:
        pass
