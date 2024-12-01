from typing import Optional, Dict, Any
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "unique_id": self.unique_id,
            "summary_id": self.summary_id,
            "transcribe_id": self.transcribe_id,
            "service_source": self.service_source,
            "date": self.date,
        }

    class Config:
        from_attributes = True


class HistoryResultDTO(BaseModel):
    id: Optional[int]
    unique_id: str
    user_id: int
    summary_text: Optional[str]
    transcribe_text: Optional[str]
    date: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "unique_id": self.unique_id,
            "summary_text": self.summary_text,
            "transcribe_text": self.transcribe_text,
            "date": self.date.strftime("%Y-%m-%dT%H:%M:%S") if self.date else None  # Преобразование datetime в строку
        }

    class Config:
        from_attributes = True
