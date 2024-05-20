from dataclasses import dataclass
from datetime import datetime
from typing import Optional





@dataclass
class TranscribedText:
    text: str
    initiator_user_id: int
    transcription_date: datetime
    transcription_time: datetime
    id: Optional[int] = None

