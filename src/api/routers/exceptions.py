from fastapi import HTTPException
from openai import BaseModel


class NotFoundError(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=404, detail=detail)


class ErrorMessage(BaseModel):
    detail: str


    class Config:
        extra = "forbid"
