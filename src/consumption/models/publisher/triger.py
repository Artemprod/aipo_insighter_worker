
from pydantic import BaseModel


class PublishTrigger(BaseModel):
    unique_id: str
    type: str
    tex_id: int
    user_id: int