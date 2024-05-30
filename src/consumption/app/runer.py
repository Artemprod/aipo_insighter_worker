
from src.consumption.app.queues.start_process import *

if __name__ == "__main__":
    asyncio.run(listener.start_consume())
