from datetime import datetime

from pydantic import BaseModel, Field


class HistoryCheckDTO(BaseModel):
    is_history: bool


class GetHistoryDTO(BaseModel):
    id: int = Field()
    unique_id: str = Field()
    user_id: int = Field()
    summary_text: str
    transcribe_text: str
    date: datetime

    class Config:
        anystr_strip_whitespace = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GetHistoryResponseList(BaseModel):
    result: list[GetHistoryDTO]
