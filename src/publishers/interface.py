from abc import ABC, abstractmethod


class IPublisher(ABC):
    @abstractmethod
    async def publish(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass
