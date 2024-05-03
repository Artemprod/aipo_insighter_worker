import asyncio

from aio_pika import IncomingMessage

from application.workers.summarizer import sum_task
from infrastructure.tasks.listen.listener import RabbitMQConnector

if __name__ == "__main__":
    listener = RabbitMQConnector('rmuser', 'rmpassword', 'localhost')

    @listener.consume('summary', 'summary_receive')
    async def process_message(message: IncomingMessage):
        print(f"Received message: {message.body.decode()}")
        await sum_task(message.body.decode())

#
    asyncio.run(process_message())