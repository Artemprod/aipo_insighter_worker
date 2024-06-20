from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class Formats(ModelBase):
    __tablename__ = 'formats'

    id = Column(Integer, primary_key=True)
    format_name = Column(String(255), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'format_name': self.format_name}