from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, BigInteger, Text, TIME, Index

from sqlalchemy.orm import relationship

from src.database.models.base_model import ModelBase


class SummaryTexts(ModelBase):
    __tablename__ = 'summary_texts'

    id = Column(BigInteger, primary_key=True)
    summary_text = Column(Text, nullable=False)
    transcribed_text_id = Column(BigInteger, ForeignKey('transcribed_texts.id'), nullable=False)
    user_id = Column(BigInteger, nullable=True)
    service_source = Column(Text, nullable=True)
    summary_date = Column(TIMESTAMP, nullable=False)

    transcribed_text = relationship('TranscribedTexts')

    def to_dict(self):
        return {
            'id': self.id,
            'summary_text': self.summary_text,
            'transcribed_text_id': self.transcribed_text_id,
            'service_source': self.service_source,
            'user_id': self.user_id,
            'summary_date': self.summary_date.isoformat(),
        }

    __table_args__ = (
        Index('ix_summary_texts_id', 'id'),
        Index('ix_summary_texts_user_id', 'user_id'),
        Index('ix_summary_texts_service_source', 'service_source'),
    )
