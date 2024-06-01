from src.database.engine.session_maker import DatabaseSessionManager


class BaseRepository:
    def __init__(self, db_session_manager: DatabaseSessionManager):
        self.db_session_manager = db_session_manager
