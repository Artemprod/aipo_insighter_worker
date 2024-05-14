from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL

from src.database.models.base_model import ModelBase

class Files(ModelBase):
    __tablename__ = 'files'

    id = Column(BigInteger, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    link = Column(String(255), nullable=False)
    format_id = Column(Integer, ForeignKey('formats.id'), nullable=False)
    duration = Column(INTERVAL)
    file_size = Column(BigInteger)
    owner_id = Column(BigInteger, nullable=False)
    upload_date = Column(TIMESTAMP, nullable=False)

    source = relationship('Sources')
    format = relationship('Formats')

    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'link': self.link,
            'format_id': self.format_id,
            'duration': str(self.duration),  # Convert INTERVAL to string for easier handling
            'file_size': self.file_size,
            'owner_id': self.owner_id,
            'upload_date': self.upload_date.isoformat()
        }
