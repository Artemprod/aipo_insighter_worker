from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase


class Stage(ModelBase):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True)
    stage_name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Stage(id={self.id}, stage_name='{self.stage_name}')>"



