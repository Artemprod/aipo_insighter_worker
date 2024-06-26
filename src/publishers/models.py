from dataclasses import dataclass

from pydantic import BaseModel


class PublishTrigger(BaseModel):
    type: str
    tex_id: int
    user_id: int
