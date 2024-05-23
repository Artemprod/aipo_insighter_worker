import asyncio
from container import listener


async def main():
    await listener.start_consume()


if __name__ == "__main__":
    asyncio.run(main())
