from abc import ABC, abstractmethod


# Абстрактный класс для загрузки файлов
class BaseFileLoader(ABC):

    @abstractmethod
    async def load(self):
        pass
