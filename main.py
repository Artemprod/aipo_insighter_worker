import asyncio
import uvicorn

from container import listener
from infrastructure.web import listen_app



async def main():
    # Создание конфигурации для Uvicorn
    config = uvicorn.Config("infrastructure.web.api_app:app", host="127.0.0.1", port=9192, lifespan="on")
    server = uvicorn.Server(config)
    # Запуск сервера и слушателя RabbitMQ конкурентно
    app_task = asyncio.create_task(server.serve())
    listener_task = asyncio.create_task(listener.start_consume())
    await asyncio.gather(app_task, listener_task)


if __name__ == "__main__":
    asyncio.run(main())
