# Абстрактный класс пайплайна
import gc


class Pipeline:
    def __init__(self, loader, file_cropper, transcriber, summarizer):
        self.loader = loader
        self.cropper = file_cropper
        self.transcriber = transcriber
        self.summarizer = summarizer

    async def run(self):
        try:
            file = await self.loader()
            bunch_of_files = await self.cropper(file)
            transcribed_text = await self.transcriber(bunch_of_files)
            summary = await self.summarizer(transcribed_text)
            return summary
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            self.cleanup()

    def cleanup(self):
        del self.loader
        del self.cropper
        del self.transcriber
        del self.summarizer
        gc.collect()
