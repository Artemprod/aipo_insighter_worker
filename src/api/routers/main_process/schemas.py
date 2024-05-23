from typing import Optional

from pydantic import BaseModel, Field


class StartFromYouTubeMessage(BaseModel):
    user_id: int = Field()
    youtube_url: str = Field()
    assistant_id: int = Field()
    publisher_queue:str = Field()
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromYouTubeErrorResponse(BaseModel):
    user_id: int = Field()
    youtube_url: str = Field()
    description: str


class StartFromStorageMessage(BaseModel):
    user_id: int = Field()
    file_path: str = Field()
    assistant_id: int = Field()
    publisher_queue: str = Field()
    storage_url: Optional[str] = None
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromStorageErrorResponse(BaseModel):
    user_id: int = Field()
    file_path: str = Field()
    storage_url: Optional[str] = None
    description: Optional[str] = None
