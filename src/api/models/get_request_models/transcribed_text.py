from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResponseTranscribedText(BaseModel):
    text: str
    initiator_user_id: int
    file_id: int
    model_id: int
    language_code: str
    id: Optional[int] = None
    tags: Optional[str] = None