from dataclasses import dataclass
from typing import Optional


@dataclass
class Status:
    status_name: str
    id: Optional[int] = None
