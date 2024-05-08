import asyncio

from application.workers.summarizer import summarize_text
from application.workers.transcriber import transcribe_youtube_video
from domain.enteties.IOdataenteties.queue_enteties import TranscribedTextId


async def pipline(youtube_url):
    r = await transcribe_youtube_video(youtube_url)
    v = TranscribedTextId.parse_raw(r)
    await summarize_text(text_id=v.id_text)


if __name__ == "__main__":
    asyncio.run(pipline(youtube_url='https://www.youtube.com/watch?v=K4z0qLg8pPg'))

