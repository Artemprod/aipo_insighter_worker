from configs import load_whisper_configs
from src.consumption.app.listener import RabbitMQConnector
from src.database.engine.session_maker import DatabaseSessionManager
from src.database.repositories.storage_container import Repositories
from src.pipelines.pipline_factory import PipelineFactory
from src.services.openai_api_package.whisper_package.whisper import WhisperClient
from src.database import *

whisper_config = load_whisper_configs()
listener = RabbitMQConnector('guest', 'guest', 5672, rabbit_host='localhost')

url = "postgresql+asyncpg://postgres:1234@localhost:5432/procees"
repositories_com = Repositories(DatabaseSessionManager(database_url=url))
whisper_client = WhisperClient(conf=whisper_config)
listener.utils.factory = PipelineFactory(repo=repositories_com, transcribe_model=whisper_client, llm="gpt-4o",
                                         max_response_tokens=4000, chunk_lents_seconds=60 * 10,
                                         server_url="nats://demo.nats.io:4222")
