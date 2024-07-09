from src.database.engine.session_maker import DatabaseSessionManager
from src.database.repositories.asssistant_repository import AssistantRepository
from src.database.repositories.history_repository import HistoryRepository
from src.database.repositories.summary_text_repository import SummaryTextRepository
from src.database.repositories.transcribed_text_repository import TranscribedTextRepository


# from src.database.repositories.work_status_repository import WorkerStatusRepository


class Repositories:
    def __init__(self, database_session_manager: DatabaseSessionManager):
        self._db_manager = database_session_manager
        self._transcribed_text_repository = TranscribedTextRepository(self._db_manager)
        self._summary_text_repository = SummaryTextRepository(self._db_manager)
        self._assistant_repository = AssistantRepository(self._db_manager)
        self._history_repository = HistoryRepository(self._db_manager)
        # self._worker_status_repository = WorkerStatusRepository(self._db_manager)

    @property
    def transcribed_text_repository(self):
        return self._transcribed_text_repository

    @property
    def summary_text_repository(self):
        return self._summary_text_repository

    @property
    def assistant_repository(self):
        return self._assistant_repository

    @property
    def history_repository(self):
        return self._history_repository
