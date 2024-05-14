from typing import Optional

from pydantic import BaseModel, Field


class StartFromYouTubeMessage(BaseModel):
    user_id: int = Field()
    youtube_url: int = Field()
    assistant_id: int = Field()
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None
