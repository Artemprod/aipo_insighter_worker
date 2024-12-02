from pydantic import BaseModel


class UserHistoryScheme(BaseModel):
    is_history: bool
