from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class SummaryTexts(ModelBase):
    __tablename__ = 'summary_texts'

    id = Column(BigInteger, primary_key=True)
    summary_text = Column(Text, nullable=False)
    transcribed_text_id = Column(BigInteger, ForeignKey('transcribed_texts.id'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    summary_date = Column(TIMESTAMP, nullable=False)
    generation_time = Column(TIME, nullable=False)
    tokens_requested = Column(Integer, nullable=False)
    tokens_generated = Column(Integer, nullable=False)

    transcribed_text = relationship('TranscribedTexts')
    model = relationship('Models')

    def to_dict(self):
        return {
            'id': self.id,
            'summary_text': self.summary_text,
            'transcribed_text_id': self.transcribed_text_id,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'summary_date': self.summary_date.isoformat(),
            'generation_time': self.generation_time.isoformat(),
            'tokens_requested': self.tokens_requested,
            'tokens_generated': self.tokens_generated
        }
