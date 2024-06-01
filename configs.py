from dataclasses import dataclass
from environs import Env

#
# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict
#
#
# class WhisperConfigs(BaseSettings):
#     whisper_model_version: str
#     whisper_language: str
#     whisper_model_temperature: str
#     model_config = SettingsConfigDict(env_file=".env", extra="ignore")
#
#
# class OpenAiConfigs(BaseSettings):
#     openai_api_key: str
#     whisper_package: WhisperConfigs = Field(default_factory=WhisperConfigs)
#     model_config = SettingsConfigDict(env_file=".env", extra="ignore")
#
# class ProjectSettings(BaseSettings):
#     open_ai: OpenAiConfigs = Field(default_factory=OpenAiConfigs)
#     model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@dataclass
class WhisperConfigs:
    api: str
    whisper_model_version: str
    whisper_language: str
    whisper_model_temperature: str


def load_whisper_configs():
    env = Env()
    env.read_env('.env')
    return WhisperConfigs(
        api=env("OPENAI_API_KEY"),
        whisper_model_version=env("WHISPER_MODEL_VERSION"),
        whisper_language=env("WHISPER_LANGUAGE"),
        whisper_model_temperature=env("WHISPER_MODEL_TEMPERATURE"),
    )
