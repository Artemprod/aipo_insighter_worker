
from src.consumption.consumers.summarizer import DocumentSummarizer
from src.consumption.consumers.transcriber import WhisperTranscriber
from src.file_manager.utils.media_file_cropper import AsyncCropper
from src.file_manager.youtube.youtube_file_loader import YouTubeFileLoader
from src.pipelines.base_pipeline import Pipeline
from src.publishers.publisher import Publisher


class PipelineFactory:

    def __init__(self, transcribe_model, llm, max_response_tokens, chunk_lents_seconds, server_url, repo):
        self.transcribe_model = transcribe_model
        self.llm = llm
        self.max_response_tokens = max_response_tokens
        self.chunk_lents_seconds = chunk_lents_seconds
        self.server_url = server_url
        self.repo = repo

    def create_youtube_pipeline(self, youtube_url, output_path, pipline_data):
        loader = YouTubeFileLoader(youtube_url, output_path)
        cropper = AsyncCropper(self.chunk_lents_seconds, output_path)
        transcriber = WhisperTranscriber(self.transcribe_model)
        summarizer = DocumentSummarizer(self.llm, self.max_response_tokens)
        publisher = Publisher(self.server_url)
        pipeline = Pipeline(self.repo, loader, cropper, transcriber, summarizer, publisher, pipline_data)
        return pipeline

    def create_storage_pipeline(self, file_path: str):
        # loader = StorageFileLoader(file_path)
        # transcriber = SimpleTranscriber()
        # summarizer = SimpleSummarizer()
        # weak_pipeline = weakref.ref(Pipeline(loader, cropper, transcriber, summarizer))
        # return weak_pipeline
        ...

#
