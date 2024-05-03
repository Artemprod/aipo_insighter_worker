import json
from contextlib import asynccontextmanager

import aio_pika
import pika
import uvicorn
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustQueue, AbstractExchange, \
    DeliveryMode
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from container import listener, postgres_database_repository
from domain.enteties.IOdataenteties.queue_enteties import Message, TranscribedTextId, SummaryTextt, \
    YoutubeTranscribationQuery, FileTranscribationQuery


@asynccontextmanager
async def lifespan(app: FastAPI):
    # инициализировать подключение к брокеру
    connection: AbstractRobustConnection = await listener.connect()
    channel: AbstractRobustChannel = await connection.channel()
    process_exchange = await channel.declare_exchange(name='processor', type='direct')
    await channel.declare_queue(name='transcribe_from_youtube_queue', durable=True)
    await channel.declare_queue(name='transcribe_from_storage_queue', durable=True)
    app.state.chanel = channel
    app.state.process_exchange = process_exchange
    yield
    # закрыть подключение к брокеру
    await connection.close()


app = FastAPI(lifespan=lifespan)


@app.post("/api/start/start_process_from_storage")
async def start_task(message: FileTranscribationQuery):
    processor_exchange_object:AbstractExchange = app.state.process_exchange
    await processor_exchange_object.publish(
        aio_pika.Message(body=message.json().encode(),
                         delivery_mode=DeliveryMode.PERSISTENT),
        routing_key='transcribe_from_storage_queue',)



@app.post("/api/start/start_process_from_youtube")
async def start_task(message: YoutubeTranscribationQuery):
    processor_exchange_object: AbstractExchange = app.state.process_exchange
    await processor_exchange_object.publish(
        aio_pika.Message(body=message.json().encode(),
                         delivery_mode=DeliveryMode.PERSISTENT),
        routing_key='transcribe_from_youtube_queue', )


@app.get("/api/results/get_transcribed_text")
async def get_transcribed_text_from_database(id_text: int):
    try:
        text = await postgres_database_repository.get_transcribed_text_by_id(result_id=id_text)
        if text is not None:

            return {"text":text.text }
        else:
            raise HTTPException(status_code=404, detail="Text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




@app.get("/api/results/get_summary_text")
async def get_summary_text_from_database(id_text: int):
    try:
        text = await postgres_database_repository.get_summary_text_by_id(result_id=id_text)
        if text is not None:

            return {"text":text.text }
        else:
            raise HTTPException(status_code=404, detail="Text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")







