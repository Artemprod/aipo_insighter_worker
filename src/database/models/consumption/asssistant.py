from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME

from src.database.models.base_model import ModelBase


class AIAssistant(ModelBase):
    __tablename__ = "ai_assistants"

    assistant_id = Column(Integer, primary_key=True, autoincrement=True)
    assistant = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    assistant_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    user_prompt_for_chunks = Column(Text)
    created_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<AIAssistant(assistant_id={self.assistant_id}, assistant='{self.assistant}', name='{self.name}')>"