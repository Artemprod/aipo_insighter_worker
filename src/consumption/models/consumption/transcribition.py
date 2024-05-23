from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TranscribedText:
    text: str
    user_id: int
    service_source: str
    transcription_date: datetime
    transcription_time: datetime
    id: Optional[int] = None

