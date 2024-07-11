import asyncio
from contextlib import asynccontextmanager

import sentry_sdk
from faststream import FastStream, ContextRepo
from faststream.rabbit import RabbitBroker, RabbitExchange

from container import settings, commands, components
from src.consumption.routers.start_process import process_router

sentry_sdk.init(
    dsn=settings.sentry.sentry_dns_worker,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    enable_tracing=True,
    debug=True
)


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
