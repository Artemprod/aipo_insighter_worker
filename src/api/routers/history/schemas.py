from datetime import datetime

from pydantic import BaseModel, Field


class HistoryCheckResponse(BaseModel):
    is_history: bool


class GetHistoryResponse(BaseModel):
    id: int = Field()
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
    result: list[GetHistoryResponse]
