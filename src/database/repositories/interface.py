
from abc import ABC, abstractmethod


class IRepositoryContainer(ABC):

    @abstractmethod
    def transcribed_text_repository(self):
        pass

    @abstractmethod
    def summary_text_repository(self):
        pass

    @abstractmethod
    def assistant_repository(self):
        pass

