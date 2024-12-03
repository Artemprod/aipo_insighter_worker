from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class HistoryDTO(BaseModel):
    id: Optional[int]
    user_id: int
    unique_id: str
    summary_id: Optional[int]
    transcribe_id: Optional[int]
    service_source: str
    date: Optional[datetime]

    class Config:
        from_attributes = True


class HistoryResultDTO(BaseModel):
    id: Optional[int]
    user_id: int
    summary_text: Optional[str]
    transcribe_text: Optional[str]
    date: Optional[datetime]

    class Config:
        from_attributes = True
