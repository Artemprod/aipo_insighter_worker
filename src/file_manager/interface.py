from abc import ABC, abstractmethod


# Абстрактный класс для загрузки файлов
class IBaseFileLoader(ABC):

    @abstractmethod
    async def load(self, url, output_path):
        pass

    async def __call__(self, url, output_path) -> str:
        return await self.load(url, output_path)