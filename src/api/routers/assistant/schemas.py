from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AssistantResultDTO(BaseModel):
    assistant_id: int
    assistant: str
    name: str
    assistant_prompt: str
    user_prompt: str
    user_prompt_for_chunks: str
    created_at: Optional[datetime]

    class Config:
        class Config:
            anystr_strip_whitespace = True
            json_encoders = {
                datetime: lambda v: v.isoformat()
            }

