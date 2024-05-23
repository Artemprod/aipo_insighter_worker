from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional





@dataclass
class SummaryText:
    summary_text: str
    transcribed_text_id: int
    user_id: int
    service_source:str
    summary_date: datetime
    id: Optional[int] = None
