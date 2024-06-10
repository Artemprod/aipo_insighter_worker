from typing import Any, List

from pydantic import Field
from pydantic.v1 import validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

load_dotenv()


class BaseConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class WhisperConfigs(BaseConfig):
    whisper_model_version: str
    whisper_model_temperature: str


class GPTConfigs(BaseConfig):
    gpt_model_version: str
    gpt_model_temperature: float
    context_length: int
    gpt_max_return_tokens: int


class AssemblyConfigs(BaseConfig):
    assembly_api_key: str
    speaker_label: bool


class OpenAiConfigs(BaseConfig):
    openai_api_key: str


class PostgresDataBaseConfigs(BaseConfig):
    postgres_url: str
    database: str


# class RabitMQExchangers(BaseConfig)

class RabitMQConfigs(BaseConfig):
    rabitmq_user: str
    rabitmq_password: str
    rabitmq_port: int
    rabitmq_host: str
    exchangers: dict





class NATSPublisherConfigs(BaseConfig):
    nats_server_url: str

class RadisConfigs(BaseConfig):
    redis_server_url: str

class ProjectSettings(BaseConfig):
    language: str
    whisper: WhisperConfigs = Field(default_factory=WhisperConfigs)
    gpt: GPTConfigs = Field(default_factory=GPTConfigs)
    assembly: AssemblyConfigs = Field(default_factory=AssemblyConfigs)
    openai: OpenAiConfigs = Field(default_factory=OpenAiConfigs)
    postgres: PostgresDataBaseConfigs = Field(default_factory=PostgresDataBaseConfigs)
    rabbitmq: RabitMQConfigs = Field(default_factory=RabitMQConfigs)
    nats_publisher: NATSPublisherConfigs = Field(default_factory=NATSPublisherConfigs)
    redis: RadisConfigs = Field(default_factory=RadisConfigs)

# print(ProjectSettings())