from dataclasses import dataclass
from datetime import datetime
from typing import Optional





@dataclass
class AIAssistant:
    assistant: str
    name: str
    assistant_prompt: str
    user_prompt: str
    user_prompt_for_chunks: Optional[str] = None
    created_at: Optional[datetime] = None
    assistant_id: Optional[int] = None
