from asyncio import sleep

from container import publisher


@publisher.publish(queue="foo")
async def sum_task(string:str):
    """

    :rtype: object
    """
    c = f'это обработанная строка {string.upper()}'
    print(f"Message Published: {c}")
    return c
