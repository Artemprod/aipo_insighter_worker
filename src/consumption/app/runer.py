import asyncio

from container import listener
from src.consumption.app.connector import Consumer
from src.consumption.app.queues.start_process import  process_message_from_youtube

async def main():

    connector = listener
    await connector.connect()

    consumers = [
        Consumer(connector, exchange='processor', queue='transcribe_from_youtube_queue', exchange_type='direct', func=process_message_from_youtube),
        Consumer(connector, exchange='processor', queue='transcribe_from_youtube_queue', exchange_type='direct', func=process_message_from_youtube),
        Consumer(connector, exchange='processor', queue='transcribe_from_youtube_queue', exchange_type='direct', func=process_message_from_youtube),
        Consumer(connector, exchange='processor', queue='transcribe_from_youtube_queue', exchange_type='direct', func=process_message_from_youtube)
    ]

    # Start consuming
    await asyncio.gather(*(consumer.start() for consumer in consumers))
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
