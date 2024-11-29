from typing import Any, Dict

from assemblyai import TranscriptionConfig
from fastapi_cache.backends.redis import RedisBackend
from project_configs.configs import ProjectSettings

from src.consumption.consumers.summarizer import DocumentSummarizer, GptSummarizer
from src.consumption.consumers.transcriber import WhisperTranscriber, AssemblyTranscriber, CostumeAssemblyTranscriber, \
    AsyncWrappedAssemblyTranscriber
from src.database.engine.session_maker import DatabaseSessionManager
from src.database.repositories.storage_container import Repositories
from src.file_manager.google_drive.google_drive_loader import GoogleDriveFileLoader
from src.file_manager.s3.s3_file_loader import S3FileLoader
from src.file_manager.utils.media_file_cropper import AsyncCropper
from src.file_manager.youtube.youtube_file_loader import YouTubeFileLoader, DLYouTubeFileLoader
from src.services.assembly.client import AssemblyClient, AsyncAssemblyClient
from src.services.openai_api_package.chat_gpt_package.client import GPTClient
from src.services.openai_api_package.chat_gpt_package.model import GPTOptions
from src.services.openai_api_package.whisper_package.whisper import WhisperClient

from redis import asyncio as aioredis
from dataclasses import dataclass

from project_configs.load_rabitmq_configs import resolved_settings


@dataclass
class SystemComponents:
    repositories_com: Any
    whisper_client: Any
    gpt_client: Any
    assembly_client: Any
    assembly_transcriber: Any
    whisper_transcriber: Any
    lang_chain_summarization: Any
    gpt_summarizer: Any
    youtube_loader: Any
    s3_loader: Any
    redis: Any
    rabit_exchangers: dict
    rabit_consumers: dict
    google_drive_loader: Any


def initialize_asyncfile_cropper():
    return AsyncCropper(chunk_lents_seconds=60 * 10)


def initialize_database_session_manager(settings: ProjectSettings):
    return DatabaseSessionManager(database_url=settings.postgres.postgres_url)


def initialize_repositories_com(settings: ProjectSettings):
    session_manager = initialize_database_session_manager(settings)
    return Repositories(database_session_manager=session_manager)


def initialize_assembly_client(settings: ProjectSettings):
    return AssemblyClient(api_key=settings.assembly.assembly_api_key)


def initialize_assembly_transcriber(settings: ProjectSettings):
    client = initialize_assembly_client(settings)
    return AssemblyTranscriber(assembly_client=client,
                               language_code=settings.language,
                               speaker_labels=settings.assembly.speaker_label)


def initialize_async_assembly_transcriber(settings: ProjectSettings):
    client = AsyncAssemblyClient(api_key=settings.assembly.assembly_api_key)
    config = TranscriptionConfig(language_code=settings.language, dual_channel=settings.assembly.speaker_label)
    return CostumeAssemblyTranscriber(client=client, config=config)


def initialize_async_wraped_assembly_transcriber(settings: ProjectSettings):
    client = AssemblyClient(api_key=settings.assembly.assembly_api_key)
    config = TranscriptionConfig(language_code=settings.language,  speaker_labels=settings.assembly.speaker_label,dual_channel=False,)
    return AsyncWrappedAssemblyTranscriber(client=client, config=config)


def initialize_whisper_client(settings: ProjectSettings):
    return WhisperClient(api_key=settings.openai.openai_api_key, configs=settings.whisper)


def initialize_whisper_transcriber(settings: ProjectSettings):
    cropper = initialize_asyncfile_cropper()
    client = initialize_whisper_client(settings)
    return WhisperTranscriber(whisper_client=client, file_cropper=cropper)


def initialize_lang_chain_summarization(settings: ProjectSettings):
    return DocumentSummarizer(model=settings.gpt.gpt_model_version,
                              max_response_tokens=settings.gpt.gpt_max_return_tokens)


def initialize_gpt_client(settings: ProjectSettings):
    return GPTClient(
        options=GPTOptions(
            host=settings.gpt.openai_host,
            port=settings.gpt.openai_port,
            api_prefix=settings.gpt.openai_api_prefix,
            single_request_endpoint=settings.gpt.openai_single_request_endpoint
        )
    )


def initialize_gpt_summarizer(settings: ProjectSettings):
    client = initialize_gpt_client(settings)
    return GptSummarizer(gpt_client=client)


def initialize_youtube_loader():
    return YouTubeFileLoader()

def initialize_dl_youtube_loader():
    return DLYouTubeFileLoader()


def initialize_s3_loader():
    return S3FileLoader()


def initialize_redis(settings: ProjectSettings):
    redis = aioredis.from_url(settings.redis.redis_server_url)
    return RedisBackend(redis)


def rabit_exchangers():
    return resolved_settings['exchangers']


def rabit_consumers():
    return resolved_settings['consumers']


def initialize_google_drive_loader():
    return GoogleDriveFileLoader()


def get_components(settings: ProjectSettings) -> SystemComponents:
    return SystemComponents(
        repositories_com=initialize_repositories_com(settings),
        whisper_client=initialize_whisper_client(settings),
        gpt_client=initialize_gpt_client(settings),
        assembly_client=initialize_assembly_client(settings),
        assembly_transcriber=initialize_async_wraped_assembly_transcriber(settings),
        whisper_transcriber=initialize_whisper_transcriber(settings),
        lang_chain_summarization=initialize_lang_chain_summarization(settings),
        gpt_summarizer=initialize_gpt_summarizer(settings),
        youtube_loader=initialize_dl_youtube_loader(),
        s3_loader=initialize_s3_loader(),
        redis=initialize_redis(settings),
        rabit_exchangers=rabit_exchangers(),
        rabit_consumers=rabit_consumers(),
        google_drive_loader=initialize_google_drive_loader(),
    )


def create_commands(system_components: SystemComponents) -> Dict[str, Dict[str, Any]]:
    commands_container = {
        "loader": {
            'youtube': system_components.youtube_loader,
            's3': system_components.s3_loader,
            'google_drive': system_components.google_drive_loader
        },
        "transcriber": {
            'whisper': system_components.whisper_transcriber,
            'assembly': system_components.assembly_transcriber
        },
        "summarizer": {
            'chat_gpt': system_components.gpt_summarizer,
            'langchain': system_components.lang_chain_summarization
        },

    }
    return commands_container





settings = ProjectSettings()
components = get_components(settings=settings)
commands = create_commands(components)
