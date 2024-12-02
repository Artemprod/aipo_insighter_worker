from typing import Optional
from pydantic import BaseModel


class BaseMessage(BaseModel):
    unique_id: str
    user_id: int
    assistant_id: int
    publisher_queue: str
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None


class StartFromYouTubeMessageScheme(BaseMessage):
    youtube_url: str


class StartFromS3Scheme(BaseMessage):
    s3_path: str
    storage_url: Optional[str] = None


class StartFromGoogleDriveScheme(BaseMessage):
    google_drive_url: str
