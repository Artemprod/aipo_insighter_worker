from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class TranscribedTexts(ModelBase):
    __tablename__ = 'transcribed_texts'

    id = Column(BigInteger, primary_key=True)
    text = Column(Text, nullable=False)
    initiator_user_id = Column(BigInteger, nullable=False)
    file_id = Column(BigInteger, ForeignKey('files.id'), nullable=False)
    transcription_date = Column(TIMESTAMP, nullable=False)
    transcription_time = Column(TIMESTAMP, nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    language_code = Column(CHAR(2))
    tags = Column(Text)

    file = relationship('Files')
    model = relationship('Models')

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'initiator_user_id': self.initiator_user_id,
            'file_id': self.file_id,
            'transcription_date': self.transcription_date.isoformat(),
            'transcription_time': self.transcription_time.isoformat(),
            'model_id': self.model_id,
            'language_code': self.language_code,
            'tags': self.tags
        }
