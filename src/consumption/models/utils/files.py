from dataclasses import dataclass
from datetime import datetime

from typing import Optional





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




