from dataclasses import dataclass
from decimal import Decimal
from typing import Optional





@dataclass
class Pricing:
    model_id: int
    cost_per_token: Decimal
    currency_id: int
    id: Optional[int] = None


