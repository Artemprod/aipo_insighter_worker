from dataclasses import dataclass
from typing import Optional





@dataclass
class Currency:
    name: str
    code: str
    id: Optional[int] = None

