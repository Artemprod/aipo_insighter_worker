import asyncio

from src.consumption.consumers.transcriber import WisperTranscriber
from src.file_manager.utils.media_file_cropper import crop_file
from src.publishers.publisher import Publisher
from src.services.youtube_package.youtube import download_video_from_youtube


#TODO Паттерн команда для пайпланов, тоесть есть серия пайплайнов и есть входящая команда и есть диспетчер для этой команды
async def youtube_pipline(youtube_url):
    file = await download_video_from_youtube(youtube_url=youtube_url,
                                             path=r"/temp")

    files = await crop_file(file_path, output_path=r"/temp")
    await WisperTranscriber.total_transcribe()
    record_id = await postgres_database_repository.save_transcribed_text(text=transcribed_text, addressee=None)

    text = TranscribedTextId(
        id_text=record_id,
        addressee=None,
        description=None,
    ).json()
    Publisher.publish_result(result=text, queue='transcribe')

    # Получить текст
    text: TranscribedText = await postgres_database_repository.get_transcribed_text_by_id(result_id=text_id)
    # Отправить в лонгченй и Получить результат саммари
    result = run_langchain(text=text.text)
    # Сохранить результат
    summary_id = await postgres_database_repository.save_summary_text(text=result, addressee=None)
    return TranscribedTextId(
        id_text=summary_id,
        addressee=None,
        description=None,
    ).json()


if __name__ == "__main__":
    asyncio.run(youtube_pipline(youtube_url='https://www.youtube.com/watch?v=K4z0qLg8pPg'))
