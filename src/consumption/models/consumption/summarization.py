from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SummaryTextScheme(BaseModel):
    summary_text: str
    user_id: int
    service_source:str
    summary_date: datetime
    id: Optional[int] = None

    class Config:
        from_attributes = True
