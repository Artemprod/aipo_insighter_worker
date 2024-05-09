from fastapi import FastAPI

from configs import load_whisper_configs
from infrastructure.api.openai_api.whisper import WhisperClient

from infrastructure.tasks.listen.listener import RabbitMQConnector
from infrastructure.tasks.send.sender import WorkerPublisher

whisper_config = load_whisper_configs()
listener = RabbitMQConnector('rmuser', 'rmpassword', 'localhost')
publisher = WorkerPublisher("nats://demo.nats.io:4222")
whisper_client = WhisperClient(conf=whisper_config)
