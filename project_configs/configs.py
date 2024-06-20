from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class BaseConfig(BaseSettings):
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class UvicornServer(BaseConfig):
    uvicorn_host: str = "0.0.0.0"


class WhisperConfigs(BaseConfig):
    whisper_model_version: str = 'whisper-1'
    whisper_model_temperature: str = '0.8'


class GPTConfigs(BaseConfig):
    gpt_model_version: Optional[str] = '3.5-turbo'
    gpt_model_temperature: Optional[float] = 1.00
    context_length: Optional[int] = 1
    gpt_max_return_tokens: Optional[int] = 1


class AssemblyConfigs(BaseConfig):
    assembly_api_key: Optional[str] = ''
    speaker_label: Optional[bool] = False


class OpenAiConfigs(BaseConfig):
    openai_api_key: str = ''


class PostgresDataBaseConfigs(BaseConfig):
    postgres_url: Optional[str]
    postgres_driver: Optional[str]
    postgres_user: Optional[str]
    postgres_password: Optional[str]
    postgres_host: Optional[str]
    postgres_port: Optional[str]
    postgres_database: Optional[str]


# class RabitMQExchangers(BaseConfig)

class RabitMQConfigs(BaseConfig):
    rabitmq_user: Optional[str] = 'guest'
    rabitmq_password: Optional[str] = 'guest'
    rabitmq_port: int = 15672
    rabitmq_host: str = 'http://localhost'


class SelectelConfigs(BaseConfig):
    access_key: str = ''
    secret_key: str = ''
    endpoint_url: str = 'https://s3.storage.selcloud.ru'
    bucket_name: str = 'private-insighter-1'


class NATSPublisherConfigs(BaseConfig):
    nats_server_url: Optional[str] = 'nats://localhost:8222'
    nats_port: Optional[str] = '8222'
    nats_host: Optional[str] = 'localhost'


class RadisConfigs(BaseConfig):
    redis_server_url: str = 'redis://'
    redis_host: str = 'localhost'
    redis_port: str = '6379'


class ProjectSettings(BaseConfig):
    language: str = 'ru'
    whisper: WhisperConfigs = Field(default_factory=WhisperConfigs)
    uvicorn_server: UvicornServer = Field(default_factory=UvicornServer)
    gpt: GPTConfigs = Field(default_factory=GPTConfigs)
    assembly: AssemblyConfigs = Field(default_factory=AssemblyConfigs)
    openai: OpenAiConfigs = Field(default_factory=OpenAiConfigs)
    postgres: PostgresDataBaseConfigs = Field(default_factory=PostgresDataBaseConfigs)
    rabbitmq: RabitMQConfigs = Field(default_factory=RabitMQConfigs)
    nats_publisher: NATSPublisherConfigs = Field(default_factory=NATSPublisherConfigs)
    redis: RadisConfigs = Field(default_factory=RadisConfigs)
    selectel: SelectelConfigs = Field(default_factory=SelectelConfigs)

print(ProjectSettings())
