from typing import Optional
from pydantic import BaseModel

from src.api.schemas import ServiceSources


class BaseMessage(BaseModel):
    unique_id: str
    user_id: int
    assistant_id: int
    publisher_queue: str
    source: Optional[str] = None
    user_prompt: Optional[str] = None
    description: Optional[str] = None
    source: ServiceSources


class StartFromYouTubeMessageScheme(BaseMessage):
    youtube_url: str


class StartFromS3Scheme(BaseMessage):
    s3_path: str
    storage_url: Optional[str] = None


class StartFromGoogleDriveScheme(BaseMessage):
    google_drive_url: str


def get_responses(source: str):
    return {
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": f"An error occurred while starting the process from {source}"}
                }
            }
        }
    }
