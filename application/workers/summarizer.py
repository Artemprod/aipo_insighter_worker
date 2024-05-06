from asyncio import sleep

from container import publisher


@publisher.publish(queue="foo")
async def summarize_text(text_id) ->str:
    #Получить текст
    #Отправить в лонгченй
    # Получить результат саммари
    #Сохранить результат
    pass