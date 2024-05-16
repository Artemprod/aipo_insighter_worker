from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase


class Pricing(ModelBase):
    __tablename__ = 'pricing'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    cost_per_token = Column(DECIMAL(10, 4), nullable=False)
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)

    model = relationship('Models')
    currency = relationship('Currencies')

    def to_dict(self):
        return {
            'id': self.id,
            'model_id': self.model_id,
            'cost_per_token': str(self.cost_per_token),
            'currency_id': self.currency_id
        }