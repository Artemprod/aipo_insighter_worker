from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    source_name: str
    id: Optional[int] = None
    domain: Optional[str] = None
