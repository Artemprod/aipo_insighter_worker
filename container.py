from configs import load_whisper_configs
from src.consumption.app.listener import RabbitMQConnector
from src.database.engine.session_maker import DatabaseSessionManager
from src.database.repositories.storage_container import Repositories
from src.services.openai_api_package.whisper_package.whisper import WhisperClient

whisper_config = load_whisper_configs()
listener = RabbitMQConnector('guest', 'guest', 5672,rabbit_host='localhost')
# publisher = WorkerPublisher("nats://demo.nats.io:4222")
whisper_client = WhisperClient(conf=whisper_config)
url = "postgresql+asyncpg://postgres:1234@localhost:5432/text_process"
repositories_com = Repositories(DatabaseSessionManager(database_url=url))