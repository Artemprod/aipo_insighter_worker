
from src.database.repositories.sql_repo import TranscribedTextRepository, SummaryTextRepository, \
    AssistantRepository, WorkerStatusRepository, DatabaseSessionManager


class Repositories:
    def __init__(self, database_session_manager :DatabaseSessionManager):
        self._db_manager = database_session_manager
        self._transcribed_text_repository = None
        self._summary_text_repository = None
        self._assistant_repository = None
        self._worker_status_repository = None

    @property
    def transcribed_text_repository(self):
        if self._transcribed_text_repository is None:
            self._transcribed_text_repository = TranscribedTextRepository(self._db_manager)
        return self._transcribed_text_repository

    @property
    def summary_text_repository(self):
        if self._summary_text_repository is None:
            self._summary_text_repository = SummaryTextRepository(self._db_manager)
        return self._summary_text_repository

    @property
    def assistant_repository(self):
        if self._assistant_repository is None:
            self._assistant_repository = AssistantRepository(self._db_manager)
        return self._assistant_repository

    @property
    def worker_status_repository(self):
        if self._worker_status_repository is None:
            self._worker_status_repository = WorkerStatusRepository(self._db_manager)
        return self._worker_status_repository
