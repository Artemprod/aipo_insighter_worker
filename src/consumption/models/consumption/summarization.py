from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional





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
