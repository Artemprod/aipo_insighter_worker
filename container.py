import os

from dotenv import load_dotenv

from configs import load_whisper_configs
from src.consumption.app.connector import RabbitMQConnector
from src.database.engine.session_maker import DatabaseSessionManager
from src.database.repositories.storage_container import Repositories
from src.pipelines.pipline_factory import PipelineFactory
from src.services.openai_api_package.whisper_package.whisper import WhisperClient

load_dotenv()

whisper_config = load_whisper_configs()
listener = RabbitMQConnector('guest', 'guest', 5672, rabbit_host='localhost')

url = os.getenv('LOCAL_URL')
repositories_com = Repositories(DatabaseSessionManager(database_url=url))
whisper_client = WhisperClient(conf=whisper_config)
listener.utils.factory = PipelineFactory(repo=repositories_com, transcribe_model=whisper_client, llm="gpt-4o",
                                         max_response_tokens=4000, chunk_length_seconds=60 * 10,
                                         server_url="nats://demo.nats.io:4222")
system = os.getenv('SYSTEM')
test_telegram_bot_token = os.getenv('TEST_TELEGRAM_BOT_TOKEN')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
