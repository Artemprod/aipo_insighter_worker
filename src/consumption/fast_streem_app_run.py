import asyncio
from contextlib import asynccontextmanager

from faststream import FastStream, ContextRepo
from faststream.rabbit import RabbitBroker, RabbitExchange

from container import settings, commands, components
from src.consumption.routers.start_process import process_router


@asynccontextmanager
async def lifespan(context: ContextRepo):
    utils = {'commands': commands,
             'database_repository': components.repositories_com}
    context.set_global("utils", utils)
    yield


async def main():
    broker = RabbitBroker(f"amqp://{settings.rabbitmq.rabitmq_user}:"
                          f"{settings.rabbitmq.rabitmq_password}@"
                          f"{settings.rabbitmq.rabitmq_host}:{settings.rabbitmq.rabitmq_port}")
    RabbitExchange(components.rabit_exchangers['process_exchanger']['name'], auto_delete=True)
    broker.include_router(process_router)
    app = FastStream(broker, lifespan=lifespan)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
