import asyncio
from pydub import AudioSegment


async def crop_file(file_path, output_path, chunk_lents_seconds=15):
    paths = []
    duration= chunk_lents_seconds * 1000
    sound = AudioSegment.from_file(file_path)
    for i, chunk in enumerate(sound[::duration]):
        save_path = fr"{output_path}\chunk_{i}.mp3"
        with open(save_path, "wb") as f:
            chunk.export(f, format="mp3")
            paths.append(save_path)
    return paths


if __name__ == '__main__':
    o_p = r'D:\projects\AIPO_V2\insighter_worker\application\services\croper\temp'
    asyncio.run(crop_file(r"C:\Users\artem\OneDrive\Рабочий стол\Тестовые данные\WEBM mini.webm",
                          output_path=o_p))
