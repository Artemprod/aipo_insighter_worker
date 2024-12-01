from abc import ABC, abstractmethod


class ICropper(ABC):

    @abstractmethod
    async def crop_file(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass
