import asyncio
from container import listener

if __name__ == "__main__":
    asyncio.run(listener.start_consume())
