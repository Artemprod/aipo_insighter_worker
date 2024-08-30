from enum import Enum


class ServiceSources(Enum):
    telegram: str = 'telegram_bot'
    web: str = 'web'
