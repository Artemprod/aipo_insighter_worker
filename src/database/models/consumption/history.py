from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.orm import relationship

from src.database.models.base_model import ModelBase


class HistoryModel(ModelBase):
    __tablename__ = 'history'

    id = Column(BigInteger, unique=True, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    unique_id = Column(String, nullable=False, index=True)
    summary_id = Column(Integer, ForeignKey('summary_texts.id'), nullable=True)
    transcribe_id = Column(Integer, ForeignKey('transcribed_texts.id'), nullable=True)
    service_source = Column(String, nullable=False, index=False)
    date = Column(TIMESTAMP, index=True)

    transcribation = relationship('TranscribedTexts', backref='history', lazy="subquery")
    summary = relationship('SummaryTexts', backref='history', lazy="subquery")

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'unique_id': self.unique_id,
            'summary_id': self.summary_id,
            'transcribe_id': self.transccribe_id,
            'date': self.date,

        }
