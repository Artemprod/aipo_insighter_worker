from dataclasses import dataclass


@dataclass
class TranscribedTextTrigger:
    tex_id: str
    user_id: int


@dataclass
class SummaryTextTrigger:
    tex_id: str
    user_id: int
