from abc import ABC, abstractmethod


class ITranscriber(ABC):
    @abstractmethod
    async def transcribe(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass


class ISummarizer(ABC):

    @abstractmethod
    async def summarize(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass