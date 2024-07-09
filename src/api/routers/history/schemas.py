from typing import Optional

from pydantic import BaseModel, Field


class GetHistoryResponse(BaseModel):
    user_id: int = Field()
