from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TranscribedText(BaseModel):
    text: str
    user_id: int
    service_source: str
    transcription_date: datetime
    transcription_time: datetime
    id: Optional[int] = None

    class Config:
        from_attributes = True
