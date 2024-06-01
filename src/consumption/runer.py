import asyncio

from container import settings, listener
from src.consumption.app.consumer import Consumer
from src.consumption.app.queues.youtube import on_message_from_youtube_queue


async def main():
    ex = list(settings.rabbitmq.exchangers.keys())[0]
    youtube_consumer = Consumer(connector=listener,
                                queue='youtube',
                                routing_key='transcribe_from_youtube_queue',
                                exchange=ex,
                                exchange_type='direct',
                                func=on_message_from_youtube_queue,
                                prefetch_count=1,
                                no_ack=False)

    await youtube_consumer.start()


if __name__ == "__main__":
    asyncio.run(main())
