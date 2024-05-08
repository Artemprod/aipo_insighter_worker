from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class Currency:
    id: int
    name: str
    code: str

@dataclass
class Pricing:
    id: int
    model_id: int
    cost_per_token: Decimal
    currency_id: int

@dataclass
class SummaryText:
    id: int
    summary_text: str
    transcribed_text_id: int
    user_id: int
    model_id: int
    summary_date: datetime
    generation_time: datetime
    tokens_requested: int
    tokens_generated: int

@dataclass
class Format:
    id: int
    format_name: str

@dataclass
class Source:
    id: int
    source_name: str
    domain: Optional[str] = None

@dataclass
class Model:
    id: int
    name: str
    version: str

@dataclass
class File:
    id: int
    source_id: int
    link: str
    format_id: int
    duration: str  # Interval presented as string for simplicity
    file_size: int
    owner_id: int
    upload_date: datetime

@dataclass
class TranscribedText:
    id: int
    text: str
    initiator_user_id: int
    file_id: int
    transcription_date: datetime
    transcription_time: datetime
    model_id: int
    language_code: str
    tags: Optional[str] = None

@dataclass
class AIAssistant:
    assistant_id: int
    assistant: str
    name: str
    assistant_prompt: str
    user_prompt: str
    user_prompt_for_chunks: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class Status:
    id: int
    status_name: str

@dataclass
class Stage:
    id: int
    stage_name: str

@dataclass
class WorkerStatus:
    id: int
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