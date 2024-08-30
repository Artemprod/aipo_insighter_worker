from datetime import datetime

from pydantic import BaseModel

from src.api.schemas import ServiceSources


class TranscriptionResultDTO(BaseModel):
    id: int
    text: str
    user_id: int
    service_source: ServiceSources
    transcription_date: datetime
    transcription_time: datetime

    class Config:
        # Указываем, что даты и времена должны быть представлены в формате ISO 8601
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SummaryResultDTO(BaseModel):
    summary_text: str
    user_id: int
    service_source: ServiceSources
    summary_date: datetime
    id: int

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResponseText(BaseModel):
    id: int | str
    initiator_user_id: int
