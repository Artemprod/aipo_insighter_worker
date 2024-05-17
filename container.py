from configs import load_whisper_configs
from src.consumption.app.listener import RabbitMQConnector



from src.publishers.publisher import WorkerPublisher

whisper_config = load_whisper_configs()
listener = RabbitMQConnector('guest', 'guest', 5672,rabbit_host='localhost')
publisher = WorkerPublisher("nats://demo.nats.io:4222")
# whisper_client = WhisperClient(conf=whisper_config)
