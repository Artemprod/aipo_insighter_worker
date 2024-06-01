from src.consumption.consumers.summarizer import DocumentSummarizer
from src.consumption.consumers.transcriber import WhisperTranscriber
from src.file_manager.utils.media_file_cropper import AsyncCropper
from src.file_manager.youtube.youtube_file_loader import YouTubeFileLoader
from src.pipelines.base_pipeline import Pipeline
from src.publishers.publisher import Publisher
from src.pipelines.models import PiplineData


class PipelineFactory:
    def __init__(self, transcribe_model, llm, max_response_tokens, chunk_length_seconds, server_url, repo):
        """
        Инициализация фабрики конвейеров.

        :param transcribe_model: Модель для транскрибирования.
        :param llm: Языковая модель для суммаризации.
        :param max_response_tokens: Максимальное количество токенов в ответе.
        :param chunk_length_seconds: Длина фрагмента в секундах.
        :param server_url: URL сервера для публикации.
        :param repo: Репозиторий для хранения данных.
        """
        self.transcribe_model = transcribe_model
        self.llm = llm
        self.max_response_tokens = max_response_tokens
        self.chunk_length_seconds = chunk_length_seconds
        self.server_url = server_url
        self.repo = repo

    def create_youtube_pipeline(self, youtube_url, output_path, pipeline_data: PiplineData):
        """
        Создание конвейера для обработки видео с YouTube.

        :param youtube_url: URL видео с YouTube.
        :param output_path: Путь для сохранения обработанных файлов.
        :param pipeline_data: Данные для конвейера.
        :return: Инициализированный конвейер.
        """
        loader = YouTubeFileLoader(youtube_url, output_path)
        cropper = AsyncCropper(self.chunk_length_seconds, output_path)
        transcriber = WhisperTranscriber(self.transcribe_model)
        summarizer = DocumentSummarizer(self.llm, self.max_response_tokens)
        publisher = Publisher(self.server_url)
        pipeline = Pipeline(self.repo, loader, cropper, transcriber, summarizer, publisher, pipeline_data)
        return pipeline

    def create_storage_pipeline(self, file_path, output_path, pipeline_data: PiplineData):
        """
        Создание конвейера для обработки видео с YouTube.

        :param file_path: PATH FILE.
        :param output_path: Путь для сохранения обработанных файлов.
        :param pipeline_data: Данные для конвейера.
        :return: Инициализированный конвейер.
        """
        loader = YouTubeFileLoader(file_path, output_path)
        cropper = AsyncCropper(self.chunk_length_seconds, output_path)
        transcriber = WhisperTranscriber(self.transcribe_model)
        summarizer = DocumentSummarizer(self.llm, self.max_response_tokens)
        publisher = Publisher(self.server_url)
        pipeline = Pipeline(self.repo, loader, cropper, transcriber, summarizer, publisher, pipeline_data)
        return pipeline
