from abc import ABC, abstractmethod


# Абстрактный класс для загрузки файлов
class IBaseFileLoader(ABC):

    @abstractmethod
    async def load(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass
