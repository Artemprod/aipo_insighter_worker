from dataclasses import dataclass


@dataclass
class PublishTrigger:
    type:str
    tex_id: str
    user_id: int


