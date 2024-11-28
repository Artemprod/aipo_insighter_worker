from abc import ABC, abstractmethod


# Абстрактный класс для загрузки файлов
class IBaseFileLoader(ABC):

    @abstractmethod
    async def load(self, url: str, output_path: str) -> str:
        pass

    async def __call__(self, url: str, output_path: str) -> str:
        return await self.load(url, output_path)