import asyncio
from functools import wraps

import nats


# TODO Добавить исходящий BaseModel клас для корректной отпроавки данныех через NATS
class WorkerPublisher:
    def __init__(self, server_url):
        self.server_url = server_url

    def publish(self, queue):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                nc = await nats.connect(self.server_url)
                result = await func(*args, **kwargs)
                await nc.publish(queue, str(result).encode())  # Убедитесь, что данные в формате bytes
                print('send to adress')
                await nc.close()

            return wrapper

        return decorator


# p = WorkerPublisher("nats://demo.nats.io:4222")


# @p.publish(queue="foo")
# async def message_handler_sum(string:str):
#     c = string.upper()
#     print(f"Message Published: {c}")
#     return c
#     # Возвращаем строку, предполагая, что это пример


# if __name__ == '__main__':
#     asyncio.run(message_handler_sum("Hello NATS!"))
