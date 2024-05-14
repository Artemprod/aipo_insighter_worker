from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class Models(ModelBase):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(255))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'version': self.version}