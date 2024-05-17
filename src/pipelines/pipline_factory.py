import asyncio
import weakref

import pytest

from container import whisper_client
from src.consumption.consumers.summarizer import DocumentSummarizer
from src.consumption.consumers.transcriber import WhisperTranscriber
from src.file_manager.utils.media_file_cropper import AsyncCropper
from src.file_manager.youtube.youtube_file_loader import YouTubeFileLoader
from src.pipelines.base_pipeline import Pipeline


class PipelineFactory:
    @staticmethod
    def create_youtube_pipeline(youtube_url, output_path, transcribe_model, llm, max_response_tokens, chunk_lents_seconds):
        loader = YouTubeFileLoader(youtube_url, output_path)
        cropper = AsyncCropper(chunk_lents_seconds,output_path)
        transcriber = WhisperTranscriber(transcribe_model)
        summarizer = DocumentSummarizer(llm, max_response_tokens)
        pipeline = Pipeline(loader, cropper, transcriber, summarizer)
        return pipeline
    @staticmethod
    def create_storage_pipeline(file_path: str):
        # loader = StorageFileLoader(file_path)
        # transcriber = SimpleTranscriber()
        # summarizer = SimpleSummarizer()
        # weak_pipeline = weakref.ref(Pipeline(loader, cropper, transcriber, summarizer))
        # return weak_pipeline
        ...





async def main():
    youtube_url = "https://www.youtube.com/watch?v=apKE_Htn_GQ"
    file_path = r"D:\projects\AIPO_V2\insighter_worker\temp"

    transcribe_model = whisper_client
    llm = "gpt-4o"
    max_response_tokens = 500
    chunk_lents_seconds = 30

    pipeline = PipelineFactory.create_youtube_pipeline(
        youtube_url, file_path, transcribe_model, llm, max_response_tokens, chunk_lents_seconds
    )
    res = await pipeline.run()
    print(res)

if __name__ == '__main__':
    asyncio.run(main())

