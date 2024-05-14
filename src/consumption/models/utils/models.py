
from dataclasses import dataclass
from typing import Optional

@dataclass
class Model:
    name: str
    version: str
    id: Optional[int] = None




