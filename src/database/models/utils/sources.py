from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class Sources(ModelBase):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    source_name = Column(String(255), nullable=False)
    domain = Column(String(255))

    def to_dict(self):
        return {'id': self.id, 'source_name': self.source_name, 'domain': self.domain}