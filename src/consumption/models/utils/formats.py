from dataclasses import dataclass
from typing import Optional





@dataclass
class Format:
    format_name: str
    id: Optional[int] = None

