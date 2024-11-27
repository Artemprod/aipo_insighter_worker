from loguru import logger
from abc import ABC, abstractmethod

from src.api.routers.main_process.schemas import BaseMessage
from src.consumption.models.consumption.queues import MessageType, UtilsType
from src.pipelines.base_pipeline import Pipeline
from src.pipelines.models import PiplineData


class BaseProcessor(ABC):
    loader_key = 'not_implemented'

    @staticmethod
    @abstractmethod
    def get_query_message(message: MessageType) -> BaseMessage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_pipeline_data(query_message: BaseMessage) -> PiplineData:
        raise NotImplementedError

    @classmethod
    async def run_pipeline(cls, pipeline: Pipeline, pipeline_data: PiplineData, message: MessageType):
        await pipeline.run(pipeline_data=pipeline_data)
        logger.info(f"Сообщение {message} обработано")

    @classmethod
    async def create_pipeline(cls, query_message: BaseMessage, utils: UtilsType):
        pipeline_data = cls.get_pipeline_data(query_message)
        pipeline = Pipeline(
            repo=utils.get("database_repository"),
            loader=utils.get("commands")['loader'][cls.loader_key],
            transcriber=utils.get("commands")['transcriber']['assembly'],
            summarizer=utils.get("commands")['summarizer']['chat_gpt'],
        )
        logger.info(f"Пайплайн данные {pipeline_data} собраны")
        logger.info(f"Пайплайн {pipeline} собран")
        return pipeline, pipeline_data

    @classmethod
    async def process_message(cls, message: MessageType) -> BaseMessage:
        logger.info(f"Received message: {message}")
        query_message = cls.get_query_message(message)
        logger.info(f"Собрал сообщение для обработки {query_message}")
        return query_message

    @classmethod
    async def handle_message(cls, message: MessageType, utils: UtilsType):
        if query_message := await cls.process_message(message):
            pipeline, pipeline_data = await cls.create_pipeline(query_message, utils)
            await cls.run_pipeline(pipeline, pipeline_data, message)
