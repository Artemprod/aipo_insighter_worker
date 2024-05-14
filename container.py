from configs import load_whisper_configs
# from infrastructure.api.openai_api_package.whisper_package import WhisperClient

from src.consumers.app.listener import RabbitMQConnector
from src.publishers.sender import WorkerPublisher

whisper_config = load_whisper_configs()
listener = RabbitMQConnector('rmuser', 'rmpassword', 'localhost')
publisher = WorkerPublisher("nats://demo.nats.io:4222")
# whisper_client = WhisperClient(conf=whisper_config)
