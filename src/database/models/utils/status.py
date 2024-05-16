from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class Status(ModelBase):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True)
    status_name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Status(id={self.id}, status_name='{self.status_name}')>"