from typing import Optional

from pydantic import BaseModel, Field


class StartFromYouTubeMessage(BaseModel):
    user_id: int = Field()
    youtube_url: str = Field()
    assistant_id: int = Field()
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromStorageMessage(BaseModel):
    user_id: int = Field()
    file_path: str = Field()
    assistant_id: int = Field()
    storage_url: Optional[str] = None
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None
