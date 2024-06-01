from pydantic import BaseModel


class Assistant(BaseModel):
    assistant_id: int
    source:str
    owner:str
    details:str
