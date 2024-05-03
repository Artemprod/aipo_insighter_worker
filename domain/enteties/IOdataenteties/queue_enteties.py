from pydantic import BaseModel


class IncomeMessage(BaseModel):
    text: str


class OtcomeMessage(BaseModel):
    text: str


class Message(BaseModel):
    name: str
    description: str | None = None


class YoutubeTranscribationQuery(BaseModel):
    url: str
    description: str | None = None


class FileTranscribationQuery(BaseModel):
    url: str
    description: str | None = None


class TranscribedText(BaseModel):
    id_text: str | int
    addressee: str | None = None
    description: str | None = None


class SummaryTextt(BaseModel):
    text: str
    description: str | None = None

class TranscribedTextId(BaseModel):
    id_text: str | int

