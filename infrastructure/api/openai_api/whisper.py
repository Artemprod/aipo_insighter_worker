# import asyncio
#
# import openai
#
# from configs import WhisperConfigs
#
#
# class WhisperClient:
#     def __init__(self, conf: WhisperConfigs):
#         """
#         Конструктор класса.
#         Инициализация API ключа и создание асинхронного клиента.
#         """
#         self.configs = conf
#
#         openai.api_key = self.configs.api
#         self.client = openai.AsyncClient()  # Обновлено с использованием правильного класса
#
#         # Инициализация базовых промптов
#         self.base_prompts = {
#             'bad_word': "Эм..Ага, так, да,да...",
#             'punctuation': "Добрый день, спасибо что пришли! Сегодня..."
#         }
#
#     async def load_prompts(self):
#         return ', '.join(self.base_prompts.values())
#
#     async def whisper_compile(self, file_path: str, additional_prompts: str = "", ):
#         with open(file_path, "rb") as audio_file:
#             whisper_args = {
#                 "model": self.configs.whisper_model_version,
#                 "prompt": f"{await self.load_prompts()}, {additional_prompts}",
#                 "file": audio_file,
#                 "language": self.configs.whisper_language,
#                 "temperature": self.configs.whisper_model_temperature,
#             }
#
#             return await self.send_request(whisper_args)
#
#     async def send_request(self, whisper_args: dict) -> str:
#         response = await self.client.audio.transcriptions.create(**whisper_args)
#         if response.text:
#             print("response from whisper received")
#         return response.text
#
# #
# # if __name__ == '__main__':
# #     async def main():
# #         c = WhisperClient(conf=configs)
# #         path = r"C:\Users\artem\OneDrive\Рабочий стол\Тестовые данные\WEBM mini.webm"
# #         a = await c.whisper_compile(file_path=path)
# #         print(a)
# #         return a
# #
# #
# #     asyncio.run(main())
