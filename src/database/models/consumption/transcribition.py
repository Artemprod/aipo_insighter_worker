from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME, Index
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import relationship

from src.database.models.base_model import ModelBase


class TranscribedTexts(ModelBase):
    __tablename__ = 'transcribed_texts'

    id = Column(BigInteger, primary_key=True)
    text = Column(Text, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    service_source = Column(Text, nullable=True)
    transcription_date = Column(TIMESTAMP, nullable=True)
    transcription_time = Column(TIMESTAMP, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'user_id': self.user_id,
            'service_source': self.service_source,
            'transcription_date': self.transcription_date.isoformat(),
            'transcription_time': self.transcription_time.isoformat(),

        }
        # Создание индексов

    __table_args__ = (
        Index('ix_transcribed_texts_id', 'id'),
        Index('ix_transcribed_texts_user_id', 'user_id'),
        Index('ix_transcribed_texts_service_source', 'service_source'),
    )
