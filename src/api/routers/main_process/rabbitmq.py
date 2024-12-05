from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange
from fastapi import Request

from container import components
from src.api.routers.main_process.schemas import BaseMessage


async def publish_message(broker: RabbitBroker, message: BaseMessage, consumer_key: str):
    await broker.publish(
        message=message.json().encode("utf-8"),
        queue=RabbitQueue(
            name=components.rabit_consumers[consumer_key]["queue"],
            routing_key=components.rabit_consumers[consumer_key]["routing_key"],
        ),
        exchange=RabbitExchange(
            components.rabit_consumers[consumer_key]["exchanger"]["name"]
        ),
    )


async def get_broker(request: Request) -> RabbitBroker:
    return request.app.state.broker
