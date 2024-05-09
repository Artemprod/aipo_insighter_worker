from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Currency:
    name: str
    code: str
    id: Optional[int] = None


@dataclass
class Pricing:
    model_id: int
    cost_per_token: Decimal
    currency_id: int
    id: Optional[int] = None


@dataclass
class SummaryText:
    summary_text: str
    transcribed_text_id: int
    user_id: int
    model_id: int
    summary_date: datetime
    generation_time: datetime
    tokens_requested: int
    tokens_generated: int
    id: Optional[int] = None


@dataclass
class Format:
    format_name: str
    id: Optional[int] = None


@dataclass
class Source:
    source_name: str
    id: Optional[int] = None
    domain: Optional[str] = None


@dataclass
class Model:
    name: str
    version: str
    id: Optional[int] = None


@dataclass
class File:
    source_id: int
    link: str
    format_id: int
    duration: str  # Interval presented as string for simplicity
    file_size: int
    owner_id: int
    upload_date: datetime
    id: Optional[int] = None


@dataclass
class TranscribedText:
    text: str
    initiator_user_id: int
    file_id: int
    transcription_date: datetime
    transcription_time: datetime
    model_id: int
    language_code: str
    id: Optional[int] = None
    text_record:Optional[int] = None
    tags: Optional[str] = None




@dataclass
class AIAssistant:
    assistant: str
    name: str
    assistant_prompt: str
    user_prompt: str
    user_prompt_for_chunks: Optional[str] = None
    created_at: Optional[datetime] = None
    assistant_id: Optional[int] = None


@dataclass
class Status:
    status_name: str
    id: Optional[int] = None


@dataclass
class Stage:
    stage_name: str
    id: Optional[int] = None


@dataclass
class WorkerStatus:
    stage_id: int
    assistant_id: int
    status_id: int
    process_id: int
    file_id: int
    user_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error_time: Optional[datetime]
    error_message: Optional[str]
    id: Optional[int] = None
