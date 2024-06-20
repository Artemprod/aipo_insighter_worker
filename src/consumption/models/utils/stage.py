from dataclasses import dataclass
from typing import Optional


@dataclass
class Stage:
    stage_name: str
    id: Optional[int] = None
