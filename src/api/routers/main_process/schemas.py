from typing import Optional

from pydantic import BaseModel, Field

from src.api.schemas import ServiceSources


class StartFromYouTubeMessage(BaseModel):
    unique_id: str = Field()
    user_id: int = Field()
    youtube_url: str = Field()
    assistant_id: int = Field()
    publisher_queue: str = Field()
    source: ServiceSources
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromYouTubeErrorResponse(BaseModel):
    user_id: int = Field()
    youtube_url: str = Field()
    description: Optional[str] = None


class StartFromStorageMessage(BaseModel):
    unique_id: str = Field()
    user_id: int = Field()
    file_path: str = Field()
    assistant_id: int = Field()
    publisher_queue: str = Field()
    storage_url: Optional[str] = None
    source: ServiceSources
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromS3(BaseModel):
    unique_id: str = Field()
    user_id: int = Field()
    s3_path: str = Field()
    assistant_id: int = Field()
    publisher_queue: str = Field()
    storage_url: Optional[str] = None
    source: ServiceSources
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromStorageErrorResponse(BaseModel):
    user_id: int = Field()
    file_path: str = Field()
    storage_url: Optional[str] = None
    description: Optional[str] = None


class StartFromYouTubeMessageResponse(BaseModel):
    status: str = Field()


class StartFromS3Response(BaseModel):
    status: str = Field()
