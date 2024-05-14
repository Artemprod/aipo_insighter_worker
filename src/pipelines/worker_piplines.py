import asyncio

from src.consumers.summarizer import summarize_text
from src.consumers.transcriber import transcribe_youtube_video
from domain.enteties.IOdataenteties.queue_enteties import TranscribedTextId

#TODO Паттерн команда для пайпланов, тоесть есть серия пайплайнов и есть входящая команда и есть диспетчер для этой команды
async def youtube_pipline(youtube_url):
    r = await transcribe_youtube_video(youtube_url)
    v = TranscribedTextId.parse_raw(r)
    await summarize_text(text_id=v.id_text)


if __name__ == "__main__":
    asyncio.run(youtube_pipline(youtube_url='https://www.youtube.com/watch?v=K4z0qLg8pPg'))

