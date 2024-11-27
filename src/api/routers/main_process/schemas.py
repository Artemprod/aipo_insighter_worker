from typing import Optional
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    unique_id: str = Field()
    user_id: int = Field()
    assistant_id: int = Field()
    publisher_queue: str = Field()
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromYouTubeMessageScheme(BaseMessage):
    youtube_url: str = Field()


class StartFromS3Scheme(BaseMessage):
    s3_path: str = Field()
    storage_url: Optional[str] = None


# Не используются. Нужно ли их оставлять?
class BaseErrorResponse(BaseModel):
    user_id: int = Field()
    description: Optional[str] = None


class StartFromYouTubeErrorResponseScheme(BaseErrorResponse):
    youtube_url: str = Field()


class StartFromStorageErrorResponseScheme(BaseErrorResponse):
    file_path: str = Field()
    storage_url: Optional[str] = None
