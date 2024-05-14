import asyncio

from application.services.croper.crop_file import crop_file
from application.services.downloader.youtube import download_video_from_youtube
from container import publisher, whisper_client, postgres_database_repository
from domain.enteties.IOdataenteties.queue_enteties import TranscribedTextId


async def total_transcribe(files: list):
    tasks = []
    for file in files:
        tasks.append(asyncio.create_task(whisper_client.whisper_compile(file_path=file)))
    result = await asyncio.gather(*tasks)
    total_transcription = " ".join(result)
    return total_transcription


# TODO Переименоваать в понятную функцию
async def transcribe(file_path):
    files = await crop_file(file_path, output_path=r"D:\projects\AIPO_V2\insighter_worker\temp")
    # Экспортировать если не экспортироавн
    # expot_to_mp3()
    print('croped')
    # ОТправить в виспер
    result = await total_transcribe(files)
    # сохранить результат в базу данных и вернуть id записи

    return result


async def download_file(url, path: str):
    return r"C:\Users\artem\OneDrive\Рабочий стол\Тестовые данные\WEBM mini.webm"


@publisher.publish(queue="transcribe")
async def transcribe_youtube_video(youtube_url: str) ->str:
    # скачать файл
    # TODO Поставить временный файлы
    file = await download_video_from_youtube(youtube_url=youtube_url,
                                             path=r"D:\projects\AIPO_V2\insighter_worker\temp")  # использует агента скачивания
    print('downloaded')
    transcribed_text: str = await transcribe(file)

    record_id = await postgres_database_repository.save_transcribed_text(text=transcribed_text, addressee=None)


    # преообразовать в данные для отправки

    return TranscribedTextId(
        id_text=record_id,
        addressee=None,
        description=None,
    ).json()


@publisher.publish(queue="transcribe")
async def transcribe_storage_file(file_url: str):
    # TODO Поставить временный файлы
    file = await download_file(url=file_url,
                               path=r"D:\projects\AIPO_V2\insighter_worker\temp")  # использует агента скачивания
    print('file downloaded')
    record_id: int = await transcribe(file)

    # преообразовать в данные для отправки
    return TranscribedTextId(
        id_text=record_id,
        addressee=None,
        description=None,
    ).json()



if __name__ == '__main__':
    async def main():
        url = "https://www.youtube.com/watch?v=HK5BRAApMp8"
        res = await transcribe_youtube_video(string=url)
        print(res)


    asyncio.run(main())
