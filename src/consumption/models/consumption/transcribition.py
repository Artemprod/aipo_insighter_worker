from dataclasses import dataclass
from datetime import datetime
from typing import Optional





@dataclass
class TranscribedText:
    text: str
    initiator_user_id: int
    file_id: int
    transcription_date: datetime
    transcription_time: datetime
    model_id: int
    language_code: str
    id: Optional[int] = None
    tags: Optional[str] = None
