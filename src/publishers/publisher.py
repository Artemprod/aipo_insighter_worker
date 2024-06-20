from dataclasses import asdict
from functools import wraps

import nats
from loguru import logger

from src.publishers.interface import IPublisher



# TODO Добавить исходящий BaseModel клас для корректной отпроавки данныех через NATS
class Publisher(IPublisher):

    def __init__(self, server_url,):
        self.server_url = server_url

    def publish_decorator(self, queue):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                nc = await nats.connect(self.server_url)
                result = await func(*args, **kwargs)
                await nc.publish(queue, str(result).encode())
                logger.info('send to address')
                await nc.close()
                return result

            return wrapper

        return decorator

    async def publish(self, result, queue):
        nc = await nats.connect(self.server_url)
        await nc.publish(queue, str(asdict(result)).encode())
        logger.info('send to adress', queue, end=' ')
        await nc.close()

    async def __call__(self, result, queue):
        await self.publish(result, queue)


