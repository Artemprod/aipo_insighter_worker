from pydantic import BaseModel, Field


class HistoryCheckResponse(BaseModel):
    is_history: bool


class GetHistoryResponse(BaseModel):
    id: int = Field()
    user_id: int = Field()
    summary_text: str
    transcribe_text: str
    date: str = Field(default='2024-07-22T14:54:46.897345')


class GetHistoryResponseList(BaseModel):
    result: list[GetHistoryResponse]
